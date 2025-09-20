#!/usr/bin/env node
/**
 * Data Processing Pipeline for Purdue CS Curriculum
 * Transforms raw scraped data into structured knowledge base
 */

const fs = require('fs').promises;
const path = require('path');

class DataProcessor {
  constructor() {
    this.courseCache = new Map();
    this.knowledgeTree = {
      root: "Purdue CS Curriculum",
      branches: {
        core_requirements: {
          courses: [],
          metadata: {
            total_credits: 0,
            typical_completion: "4 semesters"
          }
        },
        tracks: {
          machine_intelligence: {
            required: [],
            electives: {
              min_required: 3,
              options: []
            }
          },
          software_engineering: {
            required: [],
            electives: {
              min_required: 2,
              options: []
            }
          }
        }
      }
    };
  }

  async processScrapedData(rawDataPath) {
    console.log('🔄 Processing scraped data...');
    
    try {
      const rawData = JSON.parse(await fs.readFile(rawDataPath, 'utf8'));
      
      // 1. Normalize course codes
      const normalizedCourses = this.normalizeCourses(rawData.allCourses);
      
      // 2. Build knowledge tree
      this.buildKnowledgeTree(rawData, normalizedCourses);
      
      // 3. Create prerequisite mappings
      const prerequisiteMap = this.buildPrerequisiteMap(rawData.prerequisiteGraph);
      
      // 4. Generate structured output
      const processedData = {
        timestamp: new Date().toISOString(),
        source: rawData.timestamp,
        courses: normalizedCourses,
        knowledgeTree: this.knowledgeTree,
        prerequisiteMap: prerequisiteMap,
        tracks: this.processTrackData(rawData.tracks),
        statistics: this.generateStatistics(normalizedCourses)
      };
      
      return processedData;
      
    } catch (error) {
      console.error('❌ Error processing data:', error);
      throw error;
    }
  }

  normalizeCourses(courses) {
    console.log('📝 Normalizing course data...');
    
    return courses.map(course => ({
      code: course.code.replace(/\s+/g, ' ').trim(), // Normalize spacing
      title: this.cleanTitle(course.title),
      credits: this.extractCredits(course.credits || course.title),
      category: course.category || 'elective',
      prerequisites: course.prerequisites || [],
      description: course.description || ''
    }));
  }

  cleanTitle(title) {
    // Remove artifacts, instructor names, and extra formatting
    return title
      .replace(/\([^)]*\)/g, '') // Remove parentheses
      .replace(/[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+/g, '') // Remove names
      .replace(/\s+/g, ' ') // Clean whitespace
      .trim();
  }

  extractCredits(creditStr) {
    if (typeof creditStr === 'number') return creditStr;
    
    const match = String(creditStr).match(/(\d+)\s*cr/i);
    return match ? parseInt(match[1]) : 0;
  }

  buildKnowledgeTree(rawData, normalizedCourses) {
    console.log('🌳 Building knowledge tree...');
    
    // Process core requirements
    const coreCourses = rawData.coreCourses.map(course => course.code);
    this.knowledgeTree.branches.core_requirements.courses = coreCourses;
    this.knowledgeTree.branches.core_requirements.metadata.total_credits = 
      rawData.coreCourses.reduce((sum, course) => sum + (course.credits || 0), 0);
    
    // Process Machine Intelligence track
    const miTrack = rawData.tracks.machineIntelligence;
    this.knowledgeTree.branches.tracks.machine_intelligence.required = 
      miTrack.required.map(course => course.code);
    this.knowledgeTree.branches.tracks.machine_intelligence.electives.options = 
      miTrack.electives.map(course => course.code);
    
    // Process Software Engineering track
    const seTrack = rawData.tracks.softwareEngineering;
    this.knowledgeTree.branches.tracks.software_engineering.required = 
      seTrack.required.map(course => course.code);
    this.knowledgeTree.branches.tracks.software_engineering.electives.options = 
      seTrack.electives.map(course => course.code);
  }

  buildPrerequisiteMap(prerequisiteGraph) {
    console.log('🔗 Building prerequisite mappings...');
    
    const prerequisiteMap = {};
    
    prerequisiteGraph.forEach(courseNode => {
      prerequisiteMap[courseNode.code] = {
        prerequisites: courseNode.prerequisites || [],
        dependents: courseNode.dependents || []
      };
    });
    
    return prerequisiteMap;
  }

  processTrackData(tracks) {
    console.log('📚 Processing track data...');
    
    return {
      machine_intelligence: {
        name: "Machine Intelligence",
        objectives: "Prepare students for careers in artificial intelligence, machine learning, and data science",
        required_courses: tracks.machineIntelligence.required.map(course => ({
          code: course.code,
          title: course.title,
          credits: course.credits
        })),
        elective_courses: tracks.machineIntelligence.electives.map(course => ({
          code: course.code,
          title: course.title,
          credits: course.credits
        })),
        min_electives: 3,
        total_credits: this.calculateTrackCredits(tracks.machineIntelligence)
      },
      software_engineering: {
        name: "Software Engineering",
        objectives: "Prepare students for careers in software development, systems architecture, and engineering management",
        required_courses: tracks.softwareEngineering.required.map(course => ({
          code: course.code,
          title: course.title,
          credits: course.credits
        })),
        elective_courses: tracks.softwareEngineering.electives.map(course => ({
          code: course.code,
          title: course.title,
          credits: course.credits
        })),
        min_electives: 2,
        total_credits: this.calculateTrackCredits(tracks.softwareEngineering)
      }
    };
  }

  calculateTrackCredits(track) {
    const requiredCredits = track.required.reduce((sum, course) => sum + (course.credits || 0), 0);
    const electiveCredits = track.electives.reduce((sum, course) => sum + (course.credits || 0), 0);
    return requiredCredits + electiveCredits;
  }

  generateStatistics(courses) {
    console.log('📊 Generating statistics...');
    
    const stats = {
      total_courses: courses.length,
      total_credits: courses.reduce((sum, course) => sum + course.credits, 0),
      average_credits: 0,
      categories: {},
      credit_distribution: {}
    };
    
    stats.average_credits = stats.total_credits / courses.length;
    
    // Category breakdown
    courses.forEach(course => {
      stats.categories[course.category] = (stats.categories[course.category] || 0) + 1;
    });
    
    // Credit distribution
    courses.forEach(course => {
      const credits = course.credits || 0;
      stats.credit_distribution[credits] = (stats.credit_distribution[credits] || 0) + 1;
    });
    
    return stats;
  }

  async exportForN8N(processedData, outputPath) {
    console.log('🚀 Exporting data for N8N workflow...');
    
    const n8nData = {
      workflow_data: {
        courses: processedData.courses,
        tracks: processedData.tracks,
        prerequisites: processedData.prerequisiteMap
      },
      knowledge_tree: processedData.knowledgeTree,
      metadata: {
        timestamp: processedData.timestamp,
        total_courses: processedData.statistics.total_courses,
        processing_status: "completed"
      }
    };
    
    await fs.writeFile(outputPath, JSON.stringify(n8nData, null, 2));
    console.log(`✓ N8N data exported to ${outputPath}`);
  }

  async exportToPython(processedData, outputPath) {
    console.log('🐍 Exporting data for Python integration...');
    
    const pythonData = {
      courses: processedData.courses.map(course => ({
        code: course.code,
        title: course.title,
        credits: course.credits,
        prerequisites: course.prerequisites,
        description: course.description
      })),
      tracks: processedData.tracks,
      prerequisite_graph: processedData.prerequisiteMap,
      knowledge_tree: processedData.knowledgeTree
    };
    
    await fs.writeFile(outputPath, JSON.stringify(pythonData, null, 2));
    console.log(`✓ Python data exported to ${outputPath}`);
  }

  async run(inputPath, outputDir) {
    try {
      const processedData = await this.processScrapedData(inputPath);
      
      // Create output directory
      await fs.mkdir(outputDir, { recursive: true });
      
      // Export in multiple formats
      await fs.writeFile(
        path.join(outputDir, 'processed_curriculum.json'),
        JSON.stringify(processedData, null, 2)
      );
      
      await this.exportForN8N(
        processedData,
        path.join(outputDir, 'n8n_workflow_data.json')
      );
      
      await this.exportToPython(
        processedData,
        path.join(outputDir, 'python_integration_data.json')
      );
      
      console.log('\n📈 Processing Summary:');
      console.log(`├── Total courses processed: ${processedData.statistics.total_courses}`);
      console.log(`├── Total credits: ${processedData.statistics.total_credits}`);
      console.log(`├── Average credits per course: ${processedData.statistics.average_credits.toFixed(1)}`);
      console.log(`├── Categories: ${Object.keys(processedData.statistics.categories).join(', ')}`);
      console.log(`└── Export formats: JSON, N8N, Python`);
      
      return processedData;
      
    } catch (error) {
      console.error('❌ Processing failed:', error);
      throw error;
    }
  }
}

// CLI interface
if (require.main === module) {
  const { program } = require('commander');
  
  program
    .command('process <input>')
    .description('Process scraped curriculum data')
    .option('-o, --output <dir>', 'output directory', '../data/processed')
    .action(async (input, options) => {
      const processor = new DataProcessor();
      
      try {
        await processor.run(input, options.output);
        console.log('\n🎉 Data processing completed successfully!');
        
      } catch (error) {
        console.error('❌ Processing failed:', error);
        process.exit(1);
      }
    });
  
  program.parse();
}

module.exports = DataProcessor;