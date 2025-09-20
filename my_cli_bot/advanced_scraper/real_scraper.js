#!/usr/bin/env node
/**
 * Real Purdue CS Curriculum Scraper - No Mock Data
 * Uses Playwright for better browser compatibility in cloud environments
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

class RealPurdueCScraper {
  constructor() {
    this.baseUrls = {
      main: 'https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html',
      courses: 'https://www.cs.purdue.edu/academic-programs/courses/2024_fall_courses.html',
      machineIntelligence: 'https://www.cs.purdue.edu/undergraduate/curriculum/track-mI-fall2023.html',
      softwareEngineering: 'https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html',
      catalog: 'https://selfservice.mypurdue.purdue.edu/prod/bzwsrch.p_catalog_detail'
    };
    
    this.browser = null;
    this.context = null;
    this.courseCache = new Map();
    this.errors = [];
    this.metrics = {
      lastRun: null,
      coursesScraped: 0,
      failedRequests: 0,
      pagesVisited: 0
    };
    
    this.userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
  }

  async initialize() {
    console.log('🚀 Initializing Real Purdue CS Scraper...');
    
    try {
      // Launch browser with proper configuration for cloud environments
      this.browser = await chromium.launch({
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--disable-gpu',
          '--window-size=1920,1080'
        ]
      });
      
      // Create context with proper user agent
      this.context = await this.browser.newContext({
        userAgent: this.userAgent,
        viewport: { width: 1920, height: 1080 }
      });
      
      console.log('✓ Browser initialized successfully');
      return true;
      
    } catch (error) {
      console.error('❌ Browser initialization failed:', error.message);
      this.errors.push({ context: 'browser_init', error: error.message });
      return false;
    }
  }

  async scrapeCoreCurriculum() {
    console.log('📚 Scraping real core curriculum...');
    
    try {
      const page = await this.context.newPage();
      
      // Set additional headers to look more like a real browser
      await page.setExtraHTTPHeaders({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      });
      
      console.log(`   Navigating to: ${this.baseUrls.main}`);
      await page.goto(this.baseUrls.main, { 
        waitUntil: 'networkidle', 
        timeout: 60000 
      });
      
      this.metrics.pagesVisited++;
      
      // Wait for content to load
      await page.waitForTimeout(2000);
      
      // Extract course information from the page
      const courseData = await page.evaluate(() => {
        const courses = [];
        
        // Look for course tables
        const tables = document.querySelectorAll('table');
        
        tables.forEach(table => {
          const rows = table.querySelectorAll('tr');
          
          rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            
            if (cells.length >= 2) {
              const firstCell = cells[0].textContent.trim();
              const secondCell = cells[1].textContent.trim();
              
              // Match course codes like CS 18000, CS 18200, etc.
              const courseMatch = firstCell.match(/CS\s*(\d{5})/);
              
              if (courseMatch) {
                const courseCode = `CS ${courseMatch[1]}`;
                
                // Extract title (remove credits from title)
                const title = secondCell.split('(')[0].trim();
                
                // Extract credits
                const creditMatch = secondCell.match(/\((\d+)\s*cr\)/i);
                const credits = creditMatch ? parseInt(creditMatch[1]) : 0;
                
                courses.push({
                  code: courseCode,
                  title: title,
                  credits: credits,
                  category: 'core',
                  source: window.location.href
                });
              }
            }
          });
        });
        
        // Also look for course lists
        const lists = document.querySelectorAll('ul, ol');
        lists.forEach(list => {
          const items = list.querySelectorAll('li');
          
          items.forEach(item => {
            const text = item.textContent.trim();
            const courseMatch = text.match(/CS\s*(\d{5})[^\w]*(.*?)(?:\((\d+)\s*cr)?/i);
            
            if (courseMatch) {
              const courseCode = `CS ${courseMatch[1]}`;
              const title = courseMatch[2].trim();
              const credits = courseMatch[3] ? parseInt(courseMatch[3]) : 0;
              
              courses.push({
                code: courseCode,
                title: title,
                credits: credits,
                category: 'core',
                source: window.location.href
              });
            }
          });
        });
        
        return courses;
      });
      
      await page.close();
      
      // Remove duplicates
      const uniqueCourses = courseData.filter((course, index, self) => 
        index === self.findIndex(c => c.code === course.code)
      );
      
      console.log(`✓ Found ${uniqueCourses.length} core courses`);
      return uniqueCourses;
      
    } catch (error) {
      console.error('❌ Error scraping core curriculum:', error.message);
      this.errors.push({ context: 'core_curriculum', error: error.message });
      return [];
    }
  }

  async scrapeCourseListing() {
    console.log('📖 Scraping course listing...');
    
    try {
      const page = await this.context.newPage();
      
      console.log(`   Navigating to: ${this.baseUrls.courses}`);
      await page.goto(this.baseUrls.courses, { 
        waitUntil: 'networkidle', 
        timeout: 60000 
      });
      
      this.metrics.pagesVisited++;
      
      // Wait for content to load
      await page.waitForTimeout(2000);
      
      // Extract course listing
      const courseData = await page.evaluate(() => {
        const courses = [];
        
        // Look for course tables with instructor information
        const tables = document.querySelectorAll('table');
        
        tables.forEach(table => {
          const rows = table.querySelectorAll('tr');
          
          rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            
            if (cells.length >= 2) {
              const firstCell = cells[0].textContent.trim();
              const secondCell = cells[1].textContent.trim();
              
              // Match course codes
              const courseMatch = firstCell.match(/CS\s*(\d{5})/);
              
              if (courseMatch) {
                const courseCode = `CS ${courseMatch[1]}`;
                
                // Extract title (before instructor names)
                let title = secondCell;
                
                // Remove instructor names (typically capitalized names)
                title = title.replace(/[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+/g, '');
                title = title.replace(/[A-Z][a-z]+ [A-Z][a-z]+/g, '');
                title = title.trim();
                
                // Extract credits from title if present
                const creditMatch = title.match(/\((\d+)\s*cr\)/i);
                const credits = creditMatch ? parseInt(creditMatch[1]) : 3; // Default to 3 if not found
                
                // Clean title
                title = title.replace(/\(\d+\s*cr\)/i, '').trim();
                
                if (title.length > 0) {
                  courses.push({
                    code: courseCode,
                    title: title,
                    credits: credits,
                    category: 'course',
                    source: window.location.href
                  });
                }
              }
            }
          });
        });
        
        return courses;
      });
      
      await page.close();
      
      // Remove duplicates and clean data
      const uniqueCourses = courseData.filter((course, index, self) => 
        index === self.findIndex(c => c.code === course.code)
      );
      
      console.log(`✓ Found ${uniqueCourses.length} courses from listing`);
      return uniqueCourses;
      
    } catch (error) {
      console.error('❌ Error scraping course listing:', error.message);
      this.errors.push({ context: 'course_listing', error: error.message });
      return [];
    }
  }

  async scrapeTrackRequirements(trackName, trackUrl) {
    console.log(`📖 Scraping ${trackName} track requirements...`);
    
    try {
      const page = await this.context.newPage();
      
      console.log(`   Navigating to: ${trackUrl}`);
      await page.goto(trackUrl, { 
        waitUntil: 'networkidle', 
        timeout: 60000 
      });
      
      this.metrics.pagesVisited++;
      
      // Wait for content to load
      await page.waitForTimeout(2000);
      
      const trackData = await page.evaluate(() => {
        const requirements = {
          required: [],
          electives: []
        };
        
        // Look for sections with headers
        const headers = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        
        headers.forEach(header => {
          const headerText = header.textContent.toLowerCase();
          
          if (headerText.includes('required') || headerText.includes('core')) {
            // Find next element with course information
            let element = header.nextElementSibling;
            
            while (element && !element.matches('h1, h2, h3, h4, h5, h6')) {
              if (element.matches('table, ul, ol')) {
                const courses = this.extractCoursesFromElement(element);
                requirements.required.push(...courses);
                break;
              }
              element = element.nextElementSibling;
            }
          } else if (headerText.includes('elective')) {
            let element = header.nextElementSibling;
            
            while (element && !element.matches('h1, h2, h3, h4, h5, h6')) {
              if (element.matches('table, ul, ol')) {
                const courses = this.extractCoursesFromElement(element);
                requirements.electives.push(...courses);
                break;
              }
              element = element.nextElementSibling;
            }
          }
        });
        
        return requirements;
      });
      
      await page.close();
      
      console.log(`✓ Found ${trackData.required.length} required and ${trackData.electives.length} elective courses`);
      return trackData;
      
    } catch (error) {
      console.error(`❌ Error scraping ${trackName} track:`, error.message);
      this.errors.push({ context: trackName, error: error.message });
      return { required: [], electives: [] };
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
          
          const courseMatch = courseCode.match(/CS\s*(\d{5})/);
          
          if (courseMatch) {
            const code = `CS ${courseMatch[1]}`;
            const creditMatch = title.match(/\((\d+)\s*cr\)/i);
            const credits = creditMatch ? parseInt(creditMatch[1]) : 3;
            
            courses.push({
              code: code,
              title: title.replace(/\(\d+\s*cr\)/i, '').trim(),
              credits: credits
            });
          }
        }
      });
    } else if (element.tagName === 'UL' || element.tagName === 'OL') {
      const items = element.querySelectorAll('li');
      
      items.forEach(item => {
        const text = item.textContent.trim();
        const courseMatch = text.match(/CS\s*(\d{5})[^\w]*(.*?)(?:\((\d+)\s*cr)?/i);
        
        if (courseMatch) {
          const code = `CS ${courseMatch[1]}`;
          const title = courseMatch[2].trim();
          const credits = courseMatch[3] ? parseInt(courseMatch[3]) : 3;
          
          courses.push({
            code: code,
            title: title,
            credits: credits
          });
        }
      });
    }
    
    return courses;
  }

  buildPrerequisiteGraph(courses) {
    console.log('🔗 Building prerequisite graph...');
    
    const graph = new Map();
    
    // Known prerequisites based on Purdue CS curriculum
    const knownPrerequisites = {
      'CS 18000': [],
      'CS 18200': [],
      'CS 24000': ['CS 18000'],
      'CS 25000': ['CS 18200'],
      'CS 25100': ['CS 18000', 'CS 18200'],
      'CS 25200': ['CS 24000', 'CS 25000'],
      'CS 30700': ['CS 25100'],
      'CS 35200': ['CS 25200'],
      'CS 35400': ['CS 25200'],
      'CS 37300': ['CS 25100'],
      'CS 38100': ['CS 25100'],
      'CS 47100': ['CS 25100'],
      'CS 47300': ['CS 25100'],
      'CS 47800': ['CS 25100']
    };
    
    courses.forEach(course => {
      const prerequisites = knownPrerequisites[course.code] || [];
      
      graph.set(course.code, {
        ...course,
        prerequisites: prerequisites,
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
    console.log('🔄 Processing all real curriculum data...');
    
    // Scrape core curriculum
    const coreCourses = await this.scrapeCoreCurriculum();
    
    // Scrape course listing for additional details
    const courseListing = await this.scrapeCourseListing();
    
    // Scrape track requirements
    const miTrack = await this.scrapeTrackRequirements('Machine Intelligence', this.baseUrls.machineIntelligence);
    const seTrack = await this.scrapeTrackRequirements('Software Engineering', this.baseUrls.softwareEngineering);
    
    // Combine all courses
    const allCourses = [
      ...coreCourses,
      ...courseListing,
      ...miTrack.required,
      ...miTrack.electives,
      ...seTrack.required,
      ...seTrack.electives
    ];
    
    // Remove duplicates and merge information
    const courseMap = new Map();
    
    allCourses.forEach(course => {
      const existing = courseMap.get(course.code);
      
      if (existing) {
        // Merge information, preferring more complete data
        courseMap.set(course.code, {
          ...existing,
          title: course.title.length > existing.title.length ? course.title : existing.title,
          credits: course.credits > 0 ? course.credits : existing.credits,
          category: existing.category === 'core' ? 'core' : course.category
        });
      } else {
        courseMap.set(course.code, course);
      }
    });
    
    const uniqueCourses = Array.from(courseMap.values());
    
    // Build prerequisite graph
    const prerequisiteGraph = this.buildPrerequisiteGraph(uniqueCourses);
    
    // Create final data structure
    const processedData = {
      timestamp: new Date().toISOString(),
      source: 'real_scraper',
      coreCourses: coreCourses,
      courseListing: courseListing,
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
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    switch (format) {
      case 'json':
        await fs.writeFile(
          path.join(outputDir, 'real_curriculum_data.json'),
          JSON.stringify(data, null, 2)
        );
        
        // Also save timestamped backup
        await fs.writeFile(
          path.join(outputDir, `real_curriculum_data_${timestamp}.json`),
          JSON.stringify(data, null, 2)
        );
        break;
      
      case 'csv':
        const csvData = data.allCourses.map(course => 
          `"${course.code}","${course.title}",${course.credits},"${course.category}","${course.source}"`
        ).join('\n');
        
        await fs.writeFile(
          path.join(outputDir, 'real_courses.csv'),
          'code,title,credits,category,source\n' + csvData
        );
        break;
    }
    
    console.log(`✓ Real data saved in ${format} format`);
  }

  async run(options = {}) {
    const { target = 'all', format = 'json' } = options;
    
    try {
      const initialized = await this.initialize();
      
      if (!initialized) {
        console.error('❌ Failed to initialize browser');
        return null;
      }
      
      this.metrics.lastRun = new Date().toISOString();
      
      const data = await this.processAllData();
      
      await this.saveData(data, format);
      
      console.log('\n📊 Real Scraping Summary:');
      console.log(`├── Core courses: ${data.coreCourses.length}`);
      console.log(`├── Course listing: ${data.courseListing.length}`);
      console.log(`├── MI track courses: ${data.tracks.machineIntelligence.required.length + data.tracks.machineIntelligence.electives.length}`);
      console.log(`├── SE track courses: ${data.tracks.softwareEngineering.required.length + data.tracks.softwareEngineering.electives.length}`);
      console.log(`├── Total unique courses: ${data.allCourses.length}`);
      console.log(`├── Pages visited: ${this.metrics.pagesVisited}`);
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
      console.error('❌ Fatal error:', error.message);
      throw error;
    } finally {
      await this.close();
    }
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      console.log('✓ Browser closed');
    }
  }
}

module.exports = RealPurdueCScraper;

// CLI interface
if (require.main === module) {
  const { program } = require('commander');
  
  program
    .command('scrape [target]')
    .description('Scrape real Purdue CS curriculum data')
    .option('-o, --output <format>', 'output format (json|csv)', 'json')
    .action(async (target, options) => {
      const scraper = new RealPurdueCScraper();
      
      try {
        const data = await scraper.run({
          target: target || 'all',
          format: options.output
        });
        
        if (data) {
          console.log('\n🎉 Real scraping completed successfully!');
        } else {
          console.log('\n❌ Real scraping failed');
          process.exit(1);
        }
        
      } catch (error) {
        console.error('❌ Scraping failed:', error.message);
        process.exit(1);
      }
    });
  
  program.parse();
}