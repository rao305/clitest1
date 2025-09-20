#!/usr/bin/env node
/**
 * Advanced Purdue CS Curriculum Scraper with N8N Integration
 * Implements comprehensive data extraction and processing pipeline
 */

const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs').promises;
const path = require('path');

class PurdueCScraper {
  constructor() {
    this.baseUrls = {
      main: 'https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html',
      machineIntelligence: 'https://www.cs.purdue.edu/undergraduate/curriculum/track-mI-fall2023.html',
      softwareEngineering: 'https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html',
      catalog: 'https://selfservice.mypurdue.purdue.edu/prod/bzwsrch.p_catalog_detail'
    };
    
    this.browser = null;
    this.courseCache = new Map();
    this.errors = [];
    this.metrics = {
      lastRun: null,
      coursesScraped: 0,
      failedRequests: 0
    };
  }

  async initialize() {
    console.log('🚀 Initializing Purdue CS Scraper...');
    this.browser = await puppeteer.launch({ 
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    console.log('✓ Browser initialized');
  }

  async scrapeCoreCurriculum() {
    console.log('📚 Scraping core curriculum...');
    
    try {
      const page = await this.browser.newPage();
      await page.goto(this.baseUrls.main, { waitUntil: 'networkidle2' });
      
      const courseData = await page.evaluate(() => {
        const courses = [];
        
        // Look for course tables and lists
        const courseTables = document.querySelectorAll('table');
        courseTables.forEach(table => {
          const rows = table.querySelectorAll('tr');
          rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            if (cells.length >= 2) {
              const firstCell = cells[0].textContent.trim();
              const secondCell = cells[1].textContent.trim();
              
              // Check if first cell contains a course code
              if (firstCell.match(/CS\s*\d{5}/)) {
                const courseCode = firstCell.match(/CS\s*\d{5}/)[0].replace(/\s+/g, ' ');
                const title = secondCell.split('(')[0].trim();
                const creditsMatch = secondCell.match(/\((\d+)\s*cr\)/);
                const credits = creditsMatch ? parseInt(creditsMatch[1]) : 0;
                
                courses.push({
                  code: courseCode,
                  title: title,
                  credits: credits,
                  category: 'core'
                });
              }
            }
          });
        });
        
        return courses;
      });
      
      await page.close();
      console.log(`✓ Found ${courseData.length} core courses`);
      return courseData;
      
    } catch (error) {
      console.error('❌ Error scraping core curriculum:', error);
      this.errors.push({ context: 'core_curriculum', error: error.message });
      return [];
    }
  }

  async scrapeTrackRequirements(trackName, trackUrl) {
    console.log(`📖 Scraping ${trackName} track requirements...`);
    
    try {
      const page = await this.browser.newPage();
      await page.goto(trackUrl, { waitUntil: 'networkidle2' });
      
      const trackData = await page.evaluate(() => {
        const requirements = {
          required: [],
          electives: [],
          additionalRequirements: []
        };
        
        // Look for requirement sections
        const headers = document.querySelectorAll('h2, h3, h4');
        headers.forEach(header => {
          const headerText = header.textContent.toLowerCase();
          
          if (headerText.includes('required') || headerText.includes('core')) {
            // Find next table or list
            let sibling = header.nextElementSibling;
            while (sibling && !sibling.matches('table, ul, ol')) {
              sibling = sibling.nextElementSibling;
            }
            
            if (sibling) {
              const courses = this.extractCoursesFromElement(sibling);
              requirements.required.push(...courses);
            }
          } else if (headerText.includes('elective')) {
            let sibling = header.nextElementSibling;
            while (sibling && !sibling.matches('table, ul, ol')) {
              sibling = sibling.nextElementSibling;
            }
            
            if (sibling) {
              const courses = this.extractCoursesFromElement(sibling);
              requirements.electives.push(...courses);
            }
          }
        });
        
        return requirements;
      });
      
      await page.close();
      console.log(`✓ Found ${trackData.required.length} required and ${trackData.electives.length} elective courses`);
      return trackData;
      
    } catch (error) {
      console.error(`❌ Error scraping ${trackName} track:`, error);
      this.errors.push({ context: trackName, error: error.message });
      return { required: [], electives: [], additionalRequirements: [] };
    }
  }

  extractCoursesFromElement(element) {
    const courses = [];
    
    if (element.tagName === 'TABLE') {
      const rows = element.querySelectorAll('tr');
      rows.forEach(row => {
        const cells = row.querySelectorAll('td, th');
        if (cells.length >= 2) {
          const courseCode = cells[0].textContent.trim();
          const title = cells[1].textContent.trim();
          
          if (courseCode.match(/CS\s*\d{5}/)) {
            courses.push({
              code: courseCode.replace(/\s+/g, ' '),
              title: title.split('(')[0].trim(),
              credits: this.extractCredits(title)
            });
          }
        }
      });
    } else if (element.tagName === 'UL' || element.tagName === 'OL') {
      const items = element.querySelectorAll('li');
      items.forEach(item => {
        const text = item.textContent.trim();
        const courseMatch = text.match(/(CS\s*\d{5})[^\w]*(.*?)(?:\((\d+)\s*cr)?/);
        if (courseMatch) {
          courses.push({
            code: courseMatch[1].replace(/\s+/g, ' '),
            title: courseMatch[2].trim(),
            credits: courseMatch[3] ? parseInt(courseMatch[3]) : 0
          });
        }
      });
    }
    
    return courses;
  }

  extractCredits(text) {
    const creditsMatch = text.match(/\((\d+)\s*cr\)/);
    return creditsMatch ? parseInt(creditsMatch[1]) : 0;
  }

  async scrapeCourseDetails(courseCode) {
    if (this.courseCache.has(courseCode)) {
      return this.courseCache.get(courseCode);
    }
    
    try {
      const page = await this.browser.newPage();
      const catalogUrl = `${this.baseUrls.catalog}?subject=CS&term=CURRENT&cnbr=${courseCode.replace('CS ', '')}`;
      
      await page.goto(catalogUrl, { waitUntil: 'networkidle2' });
      
      const courseDetails = await page.evaluate(() => {
        return {
          title: document.querySelector('.nttitle')?.textContent?.trim() || '',
          credits: document.querySelector('.credit_hours')?.textContent?.trim() || '',
          description: document.querySelector('.courseblockdesc')?.textContent?.trim() || '',
          prerequisites: Array.from(document.querySelectorAll('.prereq')).map(el => el.textContent.trim())
        };
      });
      
      await page.close();
      
      this.courseCache.set(courseCode, courseDetails);
      this.metrics.coursesScraped++;
      
      return courseDetails;
      
    } catch (error) {
      console.error(`❌ Error scraping ${courseCode}:`, error);
      this.errors.push({ context: courseCode, error: error.message });
      this.metrics.failedRequests++;
      return null;
    }
  }

  buildPrerequisiteGraph(courses) {
    console.log('🔗 Building prerequisite graph...');
    
    const graph = new Map();
    
    courses.forEach(course => {
      graph.set(course.code, {
        ...course,
        prerequisites: course.prerequisites || [],
        dependents: []
      });
    });
    
    // Build reverse dependencies
    graph.forEach((course, code) => {
      course.prerequisites.forEach(prereq => {
        if (graph.has(prereq)) {
          graph.get(prereq).dependents.push(code);
        }
      });
    });
    
    console.log(`✓ Built graph with ${graph.size} nodes`);
    return graph;
  }

  async processAllData() {
    console.log('🔄 Processing all curriculum data...');
    
    // Scrape core curriculum
    const coreCourses = await this.scrapeCoreCurriculum();
    
    // Scrape track requirements
    const miTrack = await this.scrapeTrackRequirements('Machine Intelligence', this.baseUrls.machineIntelligence);
    const seTrack = await this.scrapeTrackRequirements('Software Engineering', this.baseUrls.softwareEngineering);
    
    // Combine all courses
    const allCourses = [
      ...coreCourses,
      ...miTrack.required,
      ...miTrack.electives,
      ...seTrack.required,
      ...seTrack.electives
    ];
    
    // Remove duplicates
    const uniqueCourses = allCourses.filter((course, index, self) => 
      index === self.findIndex(c => c.code === course.code)
    );
    
    // Build prerequisite graph
    const prerequisiteGraph = this.buildPrerequisiteGraph(uniqueCourses);
    
    // Create final data structure
    const processedData = {
      timestamp: new Date().toISOString(),
      coreCourses: coreCourses,
      tracks: {
        machineIntelligence: miTrack,
        softwareEngineering: seTrack
      },
      allCourses: uniqueCourses,
      prerequisiteGraph: Array.from(prerequisiteGraph.entries()).map(([code, data]) => ({
        code,
        ...data
      })),
      metrics: this.metrics,
      errors: this.errors
    };
    
    return processedData;
  }

  async saveData(data, format = 'json') {
    const outputDir = path.join(__dirname, '..', 'data');
    await fs.mkdir(outputDir, { recursive: true });
    
    switch (format) {
      case 'json':
        await fs.writeFile(
          path.join(outputDir, 'advanced_curriculum_data.json'),
          JSON.stringify(data, null, 2)
        );
        break;
      
      case 'csv':
        const csvData = data.allCourses.map(course => 
          `${course.code},"${course.title}",${course.credits},${course.category || 'elective'}`
        ).join('\n');
        
        await fs.writeFile(
          path.join(outputDir, 'courses.csv'),
          'code,title,credits,category\n' + csvData
        );
        break;
      
      case 'sql':
        const sqlInserts = data.allCourses.map(course => 
          `INSERT INTO courses (code, title, credits, category) VALUES ('${course.code}', '${course.title.replace(/'/g, "''")}', ${course.credits}, '${course.category || 'elective'}');`
        ).join('\n');
        
        await fs.writeFile(
          path.join(outputDir, 'courses.sql'),
          sqlInserts
        );
        break;
    }
    
    console.log(`✓ Data saved in ${format} format`);
  }

  async run(options = {}) {
    const { target = 'all', format = 'json' } = options;
    
    try {
      await this.initialize();
      
      this.metrics.lastRun = new Date().toISOString();
      
      const data = await this.processAllData();
      
      await this.saveData(data, format);
      
      console.log('\n📊 Scraping Summary:');
      console.log(`├── Core courses: ${data.coreCourses.length}`);
      console.log(`├── MI track courses: ${data.tracks.machineIntelligence.required.length + data.tracks.machineIntelligence.electives.length}`);
      console.log(`├── SE track courses: ${data.tracks.softwareEngineering.required.length + data.tracks.softwareEngineering.electives.length}`);
      console.log(`├── Total unique courses: ${data.allCourses.length}`);
      console.log(`├── Courses scraped: ${this.metrics.coursesScraped}`);
      console.log(`├── Failed requests: ${this.metrics.failedRequests}`);
      console.log(`└── Errors: ${this.errors.length}`);
      
      if (this.errors.length > 0) {
        console.log('\n⚠️  Errors encountered:');
        this.errors.forEach(error => {
          console.log(`   ${error.context}: ${error.error}`);
        });
      }
      
      return data;
      
    } catch (error) {
      console.error('❌ Fatal error:', error);
      throw error;
    } finally {
      if (this.browser) {
        await this.browser.close();
      }
    }
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

// CLI interface
if (require.main === module) {
  const { program } = require('commander');
  
  program
    .command('scrape [target]')
    .description('Scrape Purdue CS curriculum data')
    .option('-t, --track <track>', 'specific track to scrape')
    .option('-o, --output <format>', 'output format (json|csv|sql)', 'json')
    .action(async (target, options) => {
      const scraper = new PurdueCScraper();
      
      try {
        const data = await scraper.run({
          target: target || 'all',
          track: options.track,
          format: options.output
        });
        
        console.log('\n🎉 Scraping completed successfully!');
        
      } catch (error) {
        console.error('❌ Scraping failed:', error);
        process.exit(1);
      }
    });
  
  program.parse();
}

module.exports = PurdueCScraper;