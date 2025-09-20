#!/usr/bin/env node
/**
 * Command Line Interface for Advanced Purdue CS Curriculum Tools
 */

const { program } = require('commander');
const PurdueCScraper = require('./purdue_scraper');
const DataProcessor = require('./data_processor');
const N8NIntegration = require('./n8n_integration');
const CurriculumAPI = require('./api_server');

// Version information
program.version('1.0.0');

// Scraping commands
program
  .command('scrape [target]')
  .description('Scrape Purdue CS curriculum data')
  .option('-t, --track <track>', 'specific track to scrape (machine-intelligence, software-engineering)')
  .option('-o, --output <format>', 'output format (json|csv|sql)', 'json')
  .option('-v, --verbose', 'verbose output')
  .action(async (target, options) => {
    const scraper = new PurdueCScraper();
    
    if (options.verbose) {
      console.log('🔍 Starting scraper with options:', options);
    }
    
    try {
      const data = await scraper.run({
        target: target || 'all',
        track: options.track,
        format: options.output
      });
      
      console.log('\n✅ Scraping completed successfully!');
      console.log(`📊 Scraped ${data.allCourses.length} courses total`);
      
    } catch (error) {
      console.error('❌ Scraping failed:', error.message);
      process.exit(1);
    }
  });

// Data processing commands
program
  .command('process <input>')
  .description('Process scraped curriculum data')
  .option('-o, --output <dir>', 'output directory', 'data/processed')
  .option('-f, --format <format>', 'export format (json|python|n8n)', 'json')
  .action(async (input, options) => {
    const processor = new DataProcessor();
    
    try {
      const data = await processor.run(input, options.output);
      
      console.log('\n✅ Processing completed successfully!');
      console.log(`📈 Processed ${data.statistics.total_courses} courses`);
      
    } catch (error) {
      console.error('❌ Processing failed:', error.message);
      process.exit(1);
    }
  });

// N8N integration commands
program
  .command('n8n <action>')
  .description('N8N integration actions (setup|trigger|sync)')
  .option('-d, --data <path>', 'data file path for sync action')
  .action(async (action, options) => {
    const integration = new N8NIntegration();
    
    try {
      switch (action) {
        case 'setup':
          await integration.run();
          console.log('✅ N8N integration setup completed');
          break;
          
        case 'trigger':
          await integration.triggerWorkflow();
          console.log('✅ N8N workflow triggered');
          break;
          
        case 'sync':
          if (!options.data) {
            console.error('❌ Data path required for sync action');
            process.exit(1);
          }
          await integration.syncData(options.data);
          console.log('✅ Data sync completed');
          break;
          
        default:
          console.error('❌ Unknown action:', action);
          console.log('Available actions: setup, trigger, sync');
          process.exit(1);
      }
      
    } catch (error) {
      console.error(`❌ N8N ${action} failed:`, error.message);
      process.exit(1);
    }
  });

// API server commands
program
  .command('server')
  .description('Start the curriculum API server')
  .option('-p, --port <port>', 'server port', '3000')
  .action(async (options) => {
    const server = new CurriculumAPI();
    server.port = options.port;
    
    try {
      await server.start();
    } catch (error) {
      console.error('❌ Server failed to start:', error.message);
      process.exit(1);
    }
  });

// Complete pipeline command
program
  .command('pipeline')
  .description('Run complete data pipeline (scrape -> process -> serve)')
  .option('-o, --output <format>', 'output format', 'json')
  .option('-p, --port <port>', 'server port', '3000')
  .option('--skip-scrape', 'skip scraping step')
  .option('--skip-process', 'skip processing step')
  .option('--skip-server', 'skip server start')
  .action(async (options) => {
    console.log('🚀 Starting complete pipeline...\n');
    
    try {
      // Step 1: Scrape data
      if (!options.skipScrape) {
        console.log('📡 Step 1: Scraping data...');
        const scraper = new PurdueCScraper();
        await scraper.run({ format: options.output });
        console.log('✅ Scraping completed\n');
      }
      
      // Step 2: Process data
      if (!options.skipProcess) {
        console.log('⚙️ Step 2: Processing data...');
        const processor = new DataProcessor();
        await processor.run('data/advanced_curriculum_data.json', 'data/processed');
        console.log('✅ Processing completed\n');
      }
      
      // Step 3: Start server
      if (!options.skipServer) {
        console.log('🌐 Step 3: Starting API server...');
        const server = new CurriculumAPI();
        server.port = options.port;
        await server.start();
      }
      
    } catch (error) {
      console.error('❌ Pipeline failed:', error.message);
      process.exit(1);
    }
  });

// Status command
program
  .command('status')
  .description('Check system status')
  .action(async () => {
    console.log('📊 System Status Check\n');
    
    // Check data files
    const fs = require('fs').promises;
    const path = require('path');
    
    const checks = [
      { file: 'data/advanced_curriculum_data.json', description: 'Raw scraped data' },
      { file: 'data/processed/processed_curriculum.json', description: 'Processed data' },
      { file: 'data/processed/n8n_workflow_data.json', description: 'N8N workflow data' },
      { file: 'data/processed/python_integration_data.json', description: 'Python integration data' }
    ];
    
    for (const check of checks) {
      try {
        const stats = await fs.stat(check.file);
        const size = (stats.size / 1024).toFixed(2);
        console.log(`✅ ${check.description}: ${size} KB (${stats.mtime.toISOString()})`);
      } catch (error) {
        console.log(`❌ ${check.description}: Not found`);
      }
    }
    
    // Check API server
    try {
      const response = await fetch('http://localhost:3000/health');
      if (response.ok) {
        console.log('✅ API Server: Running');
      } else {
        console.log('⚠️ API Server: Not responding');
      }
    } catch (error) {
      console.log('❌ API Server: Not running');
    }
  });

// Development commands
program
  .command('dev')
  .description('Development utilities')
  .option('--test-scraper', 'test scraper functionality')
  .option('--test-api', 'test API endpoints')
  .option('--validate-data', 'validate data integrity')
  .action(async (options) => {
    if (options.testScraper) {
      console.log('🧪 Testing scraper...');
      const scraper = new PurdueCScraper();
      
      try {
        await scraper.initialize();
        const coreCourses = await scraper.scrapeCoreCurriculum();
        console.log(`✅ Found ${coreCourses.length} core courses`);
        await scraper.close();
      } catch (error) {
        console.error('❌ Scraper test failed:', error.message);
      }
    }
    
    if (options.testApi) {
      console.log('🧪 Testing API endpoints...');
      
      const endpoints = [
        '/health',
        '/api/curriculum/core',
        '/api/curriculum/tracks',
        '/api/curriculum/statistics'
      ];
      
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(`http://localhost:3000${endpoint}`);
          console.log(`${response.ok ? '✅' : '❌'} ${endpoint}: ${response.status}`);
        } catch (error) {
          console.log(`❌ ${endpoint}: Connection failed`);
        }
      }
    }
    
    if (options.validateData) {
      console.log('🧪 Validating data integrity...');
      
      try {
        const fs = require('fs').promises;
        const data = JSON.parse(await fs.readFile('data/processed/processed_curriculum.json', 'utf8'));
        
        const validation = {
          courses: data.courses?.length || 0,
          tracks: Object.keys(data.tracks || {}).length,
          prerequisites: Object.keys(data.prerequisiteMap || {}).length
        };
        
        console.log('✅ Data validation results:');
        console.log(`   Courses: ${validation.courses}`);
        console.log(`   Tracks: ${validation.tracks}`);
        console.log(`   Prerequisites: ${validation.prerequisites}`);
        
      } catch (error) {
        console.error('❌ Data validation failed:', error.message);
      }
    }
  });

// Parse command line arguments
program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}