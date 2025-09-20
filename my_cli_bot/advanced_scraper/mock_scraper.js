#!/usr/bin/env node
/**
 * Mock scraper for testing the system without browser dependencies
 */

const fs = require('fs').promises;
const path = require('path');

class MockPurdueCScraper {
  constructor() {
    this.mockData = {
      coreCourses: [
        { code: 'CS 18000', title: 'Problem Solving and Object-Oriented Programming', credits: 4, category: 'core' },
        { code: 'CS 18200', title: 'Foundations of Computer Science', credits: 3, category: 'core' },
        { code: 'CS 24000', title: 'Programming in C', credits: 3, category: 'core' },
        { code: 'CS 25000', title: 'Computer Architecture', credits: 4, category: 'core' },
        { code: 'CS 25100', title: 'Data Structures and Algorithms', credits: 3, category: 'core' },
        { code: 'CS 25200', title: 'Systems Programming', credits: 4, category: 'core' }
      ],
      tracks: {
        machineIntelligence: {
          required: [
            { code: 'CS 37300', title: 'Data Mining and Machine Learning', credits: 3 },
            { code: 'CS 47100', title: 'Introduction to Artificial Intelligence', credits: 3 }
          ],
          electives: [
            { code: 'CS 47300', title: 'Web Information Search and Management', credits: 3 },
            { code: 'CS 47800', title: 'Introduction to Bioinformatics', credits: 3 },
            { code: 'CS 49000', title: 'Deep Learning', credits: 3 }
          ]
        },
        softwareEngineering: {
          required: [
            { code: 'CS 35200', title: 'Compilers', credits: 4 },
            { code: 'CS 35400', title: 'Operating Systems', credits: 4 }
          ],
          electives: [
            { code: 'CS 40800', title: 'Software Testing', credits: 3 },
            { code: 'CS 42200', title: 'Computer Networks', credits: 3 },
            { code: 'CS 42600', title: 'Computer Security', credits: 3 }
          ]
        }
      }
    };
    
    this.metrics = {
      lastRun: null,
      coursesScraped: 0,
      failedRequests: 0
    };
    
    this.errors = [];
  }

  async initialize() {
    console.log('🚀 Initializing Mock Purdue CS Scraper...');
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate initialization
    console.log('✓ Mock scraper initialized');
  }

  async scrapeCoreCurriculum() {
    console.log('📚 Scraping core curriculum (mock)...');
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate scraping
    
    const courses = this.mockData.coreCourses;
    console.log(`✓ Found ${courses.length} core courses`);
    return courses;
  }

  async scrapeTrackRequirements(trackName, trackUrl) {
    console.log(`📖 Scraping ${trackName} track requirements (mock)...`);
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate scraping
    
    const trackKey = trackName.toLowerCase().replace(' ', '');
    const trackData = this.mockData.tracks[trackKey] || { required: [], electives: [] };
    
    console.log(`✓ Found ${trackData.required.length} required and ${trackData.electives.length} elective courses`);
    return trackData;
  }

  async scrapeCourseDetails(courseCode) {
    console.log(`🔍 Scraping details for ${courseCode} (mock)...`);
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate scraping
    
    this.metrics.coursesScraped++;
    
    return {
      title: `Mock Title for ${courseCode}`,
      credits: '3 cr',
      description: `Mock description for ${courseCode}`,
      prerequisites: this.getPrerequisites(courseCode)
    };
  }

  getPrerequisites(courseCode) {
    const prereqMap = {
      'CS 18200': [],
      'CS 18000': [],
      'CS 24000': ['CS 18000'],
      'CS 25000': ['CS 18200'],
      'CS 25100': ['CS 18000', 'CS 18200'],
      'CS 25200': ['CS 24000', 'CS 25000'],
      'CS 37300': ['CS 25100'],
      'CS 47100': ['CS 25100'],
      'CS 35200': ['CS 25200'],
      'CS 35400': ['CS 25200']
    };
    
    return prereqMap[courseCode] || [];
  }

  buildPrerequisiteGraph(courses) {
    console.log('🔗 Building prerequisite graph...');
    
    const graph = new Map();
    
    courses.forEach(course => {
      const prerequisites = this.getPrerequisites(course.code);
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
    console.log('🔄 Processing all curriculum data (mock)...');
    
    // Scrape core curriculum
    const coreCourses = await this.scrapeCoreCurriculum();
    
    // Scrape track requirements
    const miTrack = await this.scrapeTrackRequirements('Machine Intelligence', '');
    const seTrack = await this.scrapeTrackRequirements('Software Engineering', '');
    
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
      
      console.log('\n📊 Mock Scraping Summary:');
      console.log(`├── Core courses: ${data.coreCourses.length}`);
      console.log(`├── MI track courses: ${data.tracks.machineIntelligence.required.length + data.tracks.machineIntelligence.electives.length}`);
      console.log(`├── SE track courses: ${data.tracks.softwareEngineering.required.length + data.tracks.softwareEngineering.electives.length}`);
      console.log(`├── Total unique courses: ${data.allCourses.length}`);
      console.log(`├── Courses scraped: ${this.metrics.coursesScraped}`);
      console.log(`├── Failed requests: ${this.metrics.failedRequests}`);
      console.log(`└── Errors: ${this.errors.length}`);
      
      return data;
      
    } catch (error) {
      console.error('❌ Fatal error:', error);
      throw error;
    }
  }

  async close() {
    console.log('✓ Mock scraper closed');
  }
}

module.exports = MockPurdueCScraper;