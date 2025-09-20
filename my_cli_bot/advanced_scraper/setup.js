#!/usr/bin/env node
/**
 * Setup script for Advanced Purdue CS Curriculum System
 */

const fs = require('fs').promises;
const path = require('path');
const PurdueCScraper = require('./purdue_scraper');
const DataProcessor = require('./data_processor');
const N8NIntegration = require('./n8n_integration');

class SystemSetup {
  constructor() {
    this.baseDir = path.join(__dirname, '..');
    this.dataDir = path.join(this.baseDir, 'data');
    this.processedDir = path.join(this.dataDir, 'processed');
    this.n8nDir = path.join(this.dataDir, 'n8n');
  }

  async createDirectories() {
    console.log('📁 Creating directory structure...');
    
    const dirs = [
      this.dataDir,
      this.processedDir,
      this.n8nDir,
      path.join(this.baseDir, 'logs'),
      path.join(this.baseDir, 'cache')
    ];
    
    for (const dir of dirs) {
      await fs.mkdir(dir, { recursive: true });
      console.log(`   ✓ ${dir}`);
    }
  }

  async createPackageJson() {
    console.log('📦 Creating package.json...');
    
    const packageData = {
      name: "purdue-cs-curriculum-scraper",
      version: "1.0.0",
      description: "Advanced Purdue CS Curriculum Scraper with N8N Integration",
      main: "cli.js",
      scripts: {
        "start": "node cli.js",
        "scrape": "node cli.js scrape",
        "process": "node cli.js process",
        "server": "node cli.js server",
        "pipeline": "node cli.js pipeline",
        "status": "node cli.js status",
        "test": "node cli.js dev --test-scraper --test-api --validate-data"
      },
      keywords: ["purdue", "cs", "curriculum", "scraper", "n8n", "education"],
      author: "Replit AI",
      license: "MIT",
      dependencies: {
        "puppeteer": "^21.0.0",
        "cheerio": "^1.0.0-rc.12",
        "express": "^4.18.0",
        "commander": "^11.0.0",
        "pg": "^8.11.0"
      },
      bin: {
        "purdue-scraper": "./cli.js"
      }
    };
    
    const packagePath = path.join(__dirname, 'package.json');
    await fs.writeFile(packagePath, JSON.stringify(packageData, null, 2));
    console.log('   ✓ package.json created');
  }

  async createConfiguration() {
    console.log('⚙️ Creating configuration files...');
    
    const config = {
      scraper: {
        baseUrls: {
          main: 'https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html',
          machineIntelligence: 'https://www.cs.purdue.edu/undergraduate/curriculum/track-mI-fall2023.html',
          softwareEngineering: 'https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html'
        },
        timeouts: {
          pageLoad: 30000,
          navigation: 10000
        },
        retryAttempts: 3,
        concurrent: false
      },
      processor: {
        outputFormats: ['json', 'python', 'n8n'],
        validation: {
          minCourses: 50,
          requiredTracks: ['machine_intelligence', 'software_engineering']
        }
      },
      n8n: {
        webhookUrl: process.env.N8N_WEBHOOK_URL || 'http://localhost:5678/webhook/purdue-cs',
        workflowId: process.env.N8N_WORKFLOW_ID || 'purdue-cs-curriculum',
        schedule: '0 0 * * 0'
      },
      api: {
        port: 3000,
        cors: true,
        rateLimit: {
          windowMs: 15 * 60 * 1000,
          max: 100
        }
      }
    };
    
    const configPath = path.join(this.dataDir, 'config.json');
    await fs.writeFile(configPath, JSON.stringify(config, null, 2));
    console.log('   ✓ Configuration file created');
  }

  async createDockerCompose() {
    console.log('🐳 Creating Docker Compose configuration...');
    
    const dockerCompose = `version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    container_name: purdue-n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=\${N8N_PASSWORD:-admin}
      - N8N_WEBHOOK_URL=http://localhost:5678/webhook/
      - N8N_PROTOCOL=http
      - N8N_HOST=localhost
      - N8N_PORT=5678
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n/workflows:/home/node/.n8n/workflows
    depends_on:
      - postgres

  postgres:
    image: postgres:13
    container_name: purdue-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=purdue_cs
      - POSTGRES_USER=\${POSTGRES_USER:-admin}
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD:-password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  scraper:
    build: .
    container_name: purdue-scraper
    restart: unless-stopped
    depends_on:
      - postgres
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://\${POSTGRES_USER:-admin}:\${POSTGRES_PASSWORD:-password}@postgres:5432/purdue_cs
      - N8N_WEBHOOK_URL=http://n8n:5678/webhook/purdue-cs
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    command: ["node", "cli.js", "pipeline"]

volumes:
  n8n_data:
  postgres_data:
`;
    
    const dockerComposePath = path.join(this.baseDir, 'docker-compose.yml');
    await fs.writeFile(dockerComposePath, dockerCompose);
    console.log('   ✓ Docker Compose file created');
  }

  async createEnvTemplate() {
    console.log('📄 Creating environment template...');
    
    const envTemplate = `# Purdue CS Curriculum Scraper Environment Variables

# Database Configuration
DATABASE_URL=postgresql://admin:password@localhost:5432/purdue_cs
POSTGRES_USER=admin
POSTGRES_PASSWORD=password

# N8N Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook/purdue-cs
N8N_WORKFLOW_ID=purdue-cs-curriculum
N8N_PASSWORD=admin

# API Configuration
API_PORT=3000
API_CORS_ORIGIN=*

# Scraper Configuration
SCRAPER_TIMEOUT=30000
SCRAPER_RETRY_ATTEMPTS=3
SCRAPER_CONCURRENT=false

# Environment
NODE_ENV=development
LOG_LEVEL=info
`;
    
    const envPath = path.join(this.baseDir, '.env.template');
    await fs.writeFile(envPath, envTemplate);
    console.log('   ✓ Environment template created');
  }

  async createDatabase() {
    console.log('🗄️ Creating database schema...');
    
    const schema = `-- Purdue CS Curriculum Database Schema

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(300) NOT NULL,
    credits INTEGER DEFAULT 0,
    description TEXT,
    category VARCHAR(50) DEFAULT 'elective',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracks table
CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    objectives TEXT,
    min_electives INTEGER DEFAULT 0,
    total_credits INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track requirements table
CREATE TABLE IF NOT EXISTS track_requirements (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
    course_code VARCHAR(20) REFERENCES courses(code) ON DELETE CASCADE,
    requirement_type VARCHAR(20) CHECK (requirement_type IN ('required', 'elective')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prerequisites table
CREATE TABLE IF NOT EXISTS prerequisites (
    id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) REFERENCES courses(code) ON DELETE CASCADE,
    prerequisite_code VARCHAR(20) REFERENCES courses(code) ON DELETE CASCADE,
    requirement_type VARCHAR(20) DEFAULT 'mandatory',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scraping logs table
CREATE TABLE IF NOT EXISTS scraping_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    courses_scraped INTEGER DEFAULT 0,
    tracks_scraped INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    details JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(code);
CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category);
CREATE INDEX IF NOT EXISTS idx_track_requirements_track ON track_requirements(track_id);
CREATE INDEX IF NOT EXISTS idx_track_requirements_course ON track_requirements(course_code);
CREATE INDEX IF NOT EXISTS idx_prerequisites_course ON prerequisites(course_code);
CREATE INDEX IF NOT EXISTS idx_prerequisites_prereq ON prerequisites(prerequisite_code);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_timestamp ON scraping_logs(timestamp);

-- Insert default tracks
INSERT INTO tracks (name, display_name, objectives, min_electives, total_credits) 
VALUES 
    ('machine_intelligence', 'Machine Intelligence', 'Prepare students for careers in artificial intelligence, machine learning, and data science', 3, 9),
    ('software_engineering', 'Software Engineering', 'Prepare students for careers in software development, systems architecture, and engineering management', 2, 8)
ON CONFLICT (name) DO NOTHING;
`;
    
    const schemaPath = path.join(this.dataDir, 'init.sql');
    await fs.writeFile(schemaPath, schema);
    console.log('   ✓ Database schema created');
  }

  async runInitialScrape() {
    console.log('🚀 Running initial data scrape...');
    
    try {
      const scraper = new PurdueCScraper();
      const data = await scraper.run({ format: 'json' });
      
      console.log(`   ✓ Scraped ${data.allCourses.length} courses`);
      console.log(`   ✓ Found ${Object.keys(data.tracks).length} tracks`);
      
      return data;
    } catch (error) {
      console.error('   ❌ Initial scrape failed:', error.message);
      return null;
    }
  }

  async processInitialData() {
    console.log('⚙️ Processing initial data...');
    
    try {
      const processor = new DataProcessor();
      const data = await processor.run(
        path.join(this.dataDir, 'advanced_curriculum_data.json'),
        this.processedDir
      );
      
      console.log(`   ✓ Processed ${data.statistics.total_courses} courses`);
      console.log(`   ✓ Generated ${Object.keys(data.tracks).length} track definitions`);
      
      return data;
    } catch (error) {
      console.error('   ❌ Data processing failed:', error.message);
      return null;
    }
  }

  async setupN8NIntegration() {
    console.log('🔄 Setting up N8N integration...');
    
    try {
      const integration = new N8NIntegration();
      await integration.run();
      
      console.log('   ✓ N8N workflow created');
      console.log('   ✓ Data pipeline configured');
      console.log('   ✓ Monitoring setup complete');
      
      return true;
    } catch (error) {
      console.error('   ❌ N8N setup failed:', error.message);
      return false;
    }
  }

  async generateReadme() {
    console.log('📚 Generating README documentation...');
    
    const readme = `# Purdue CS Curriculum Scraper

Advanced web scraping system for Purdue Computer Science curriculum data with N8N workflow automation.

## Features

- **Comprehensive Data Extraction**: Scrapes course information, prerequisites, and track requirements
- **N8N Integration**: Automated workflow scheduling and data processing
- **RESTful API**: Provides programmatic access to curriculum data
- **Multiple Output Formats**: JSON, CSV, SQL, and Python integration formats
- **Data Validation**: Ensures data quality and completeness
- **Knowledge Graph**: Structured prerequisite relationships

## Quick Start

\`\`\`bash
# Install dependencies
npm install

# Run complete pipeline
npm run pipeline

# Start API server
npm run server

# Check system status
npm run status
\`\`\`

## Commands

### Scraping
\`\`\`bash
# Scrape all curriculum data
node cli.js scrape

# Scrape specific track
node cli.js scrape --track machine-intelligence

# Output in different formats
node cli.js scrape --output csv
\`\`\`

### Data Processing
\`\`\`bash
# Process scraped data
node cli.js process data/advanced_curriculum_data.json

# Custom output directory
node cli.js process data/input.json --output custom/output/dir
\`\`\`

### N8N Integration
\`\`\`bash
# Setup N8N workflow
node cli.js n8n setup

# Trigger workflow manually
node cli.js n8n trigger

# Sync data with N8N
node cli.js n8n sync data/processed/processed_curriculum.json
\`\`\`

### API Server
\`\`\`bash
# Start server on default port (3000)
node cli.js server

# Start on custom port
node cli.js server --port 8080
\`\`\`

## API Endpoints

- \`GET /api/curriculum/core\` - Core CS requirements
- \`GET /api/curriculum/tracks\` - Available tracks
- \`GET /api/curriculum/tracks/:trackName\` - Track details
- \`GET /api/curriculum/course/:courseCode\` - Course information
- \`GET /api/curriculum/prerequisites/:courseCode\` - Prerequisite chain
- \`GET /api/curriculum/search\` - Search courses
- \`POST /api/curriculum/validate-schedule\` - Schedule validation

## Configuration

Copy \`.env.template\` to \`.env\` and customize:

\`\`\`env
DATABASE_URL=postgresql://admin:password@localhost:5432/purdue_cs
N8N_WEBHOOK_URL=http://localhost:5678/webhook/purdue-cs
API_PORT=3000
\`\`\`

## Docker Deployment

\`\`\`bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
\`\`\`

## Development

\`\`\`bash
# Test scraper
node cli.js dev --test-scraper

# Test API
node cli.js dev --test-api

# Validate data
node cli.js dev --validate-data
\`\`\`

## Architecture

The system consists of four main components:

1. **Scraper**: Extracts data from Purdue CS websites
2. **Processor**: Transforms raw data into structured formats
3. **N8N Integration**: Automates workflows and scheduling
4. **API Server**: Provides RESTful access to data

## Data Flow

1. Scraper extracts curriculum data from Purdue websites
2. Processor transforms and validates the data
3. N8N workflows manage automated updates and monitoring
4. API server provides real-time access to processed data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: \`npm test\`
5. Submit a pull request

## License

MIT License - see LICENSE file for details
`;
    
    const readmePath = path.join(this.baseDir, 'README.md');
    await fs.writeFile(readmePath, readme);
    console.log('   ✓ README.md generated');
  }

  async run() {
    console.log('🚀 Setting up Advanced Purdue CS Curriculum System\n');
    
    try {
      // Create directory structure
      await this.createDirectories();
      
      // Create configuration files
      await this.createPackageJson();
      await this.createConfiguration();
      await this.createDockerCompose();
      await this.createEnvTemplate();
      await this.createDatabase();
      
      // Run initial scrape
      const scrapeData = await this.runInitialScrape();
      
      // Process initial data
      if (scrapeData) {
        await this.processInitialData();
      }
      
      // Setup N8N integration
      await this.setupN8NIntegration();
      
      // Generate documentation
      await this.generateReadme();
      
      console.log('\n🎉 Setup completed successfully!');
      console.log('');
      console.log('📋 Next steps:');
      console.log('1. Copy .env.template to .env and customize');
      console.log('2. Run: npm run pipeline');
      console.log('3. Access API at: http://localhost:3000');
      console.log('4. Access N8N at: http://localhost:5678');
      console.log('');
      console.log('🔧 Available commands:');
      console.log('- npm run scrape     # Scrape curriculum data');
      console.log('- npm run process    # Process scraped data');
      console.log('- npm run server     # Start API server');
      console.log('- npm run status     # Check system status');
      console.log('- npm test           # Run all tests');
      
    } catch (error) {
      console.error('❌ Setup failed:', error.message);
      process.exit(1);
    }
  }
}

// Run setup if called directly
if (require.main === module) {
  const setup = new SystemSetup();
  setup.run();
}

module.exports = SystemSetup;