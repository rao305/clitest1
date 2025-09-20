#!/usr/bin/env node
/**
 * Express API Server for Purdue CS Curriculum Data
 * Provides RESTful endpoints for curriculum information
 */

const express = require('express');
const fs = require('fs').promises;
const path = require('path');

class CurriculumAPI {
  constructor() {
    this.app = express();
    this.port = process.env.PORT || 3000;
    this.dataPath = path.join(__dirname, '..', 'data', 'processed');
    this.curriculumData = null;
    
    this.setupMiddleware();
    this.setupRoutes();
  }

  setupMiddleware() {
    this.app.use(express.json());
    this.app.use(express.static('public'));
    
    // CORS middleware
    this.app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
      next();
    });
  }

  async loadData() {
    try {
      const dataFile = path.join(this.dataPath, 'processed_curriculum.json');
      const data = await fs.readFile(dataFile, 'utf8');
      this.curriculumData = JSON.parse(data);
      console.log('✓ Curriculum data loaded');
    } catch (error) {
      console.error('❌ Error loading curriculum data:', error);
      this.curriculumData = { courses: [], tracks: {}, prerequisiteMap: {} };
    }
  }

  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'healthy',
        timestamp: new Date().toISOString(),
        dataLoaded: !!this.curriculumData
      });
    });

    // Core curriculum requirements
    this.app.get('/api/curriculum/core', (req, res) => {
      try {
        const coreCourses = this.curriculumData.knowledgeTree.branches.core_requirements.courses;
        const courseDetails = coreCourses.map(code => 
          this.curriculumData.courses.find(course => course.code === code)
        ).filter(Boolean);
        
        res.json({
          courses: courseDetails,
          metadata: this.curriculumData.knowledgeTree.branches.core_requirements.metadata
        });
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch core requirements' });
      }
    });

    // Track requirements
    this.app.get('/api/curriculum/tracks/:trackName', (req, res) => {
      try {
        const trackName = req.params.trackName.toLowerCase().replace('-', '_');
        const track = this.curriculumData.tracks[trackName];
        
        if (!track) {
          return res.status(404).json({ error: 'Track not found' });
        }
        
        res.json(track);
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch track requirements' });
      }
    });

    // Available tracks
    this.app.get('/api/curriculum/tracks', (req, res) => {
      try {
        const tracks = Object.keys(this.curriculumData.tracks).map(key => ({
          id: key,
          name: this.curriculumData.tracks[key].name,
          objectives: this.curriculumData.tracks[key].objectives
        }));
        
        res.json({ tracks });
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch tracks' });
      }
    });

    // Course details
    this.app.get('/api/curriculum/course/:courseCode', (req, res) => {
      try {
        const courseCode = req.params.courseCode.toUpperCase();
        const course = this.curriculumData.courses.find(c => c.code === courseCode);
        
        if (!course) {
          return res.status(404).json({ error: 'Course not found' });
        }
        
        // Add prerequisite information
        const prerequisites = this.curriculumData.prerequisiteMap[courseCode];
        
        res.json({
          ...course,
          prerequisites: prerequisites?.prerequisites || [],
          dependents: prerequisites?.dependents || []
        });
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch course details' });
      }
    });

    // Prerequisites chain
    this.app.get('/api/curriculum/prerequisites/:courseCode', (req, res) => {
      try {
        const courseCode = req.params.courseCode.toUpperCase();
        const prerequisites = this.getPrerequisiteChain(courseCode);
        
        res.json({
          course: courseCode,
          prerequisites: prerequisites
        });
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch prerequisite chain' });
      }
    });

    // Course roadmap for track
    this.app.get('/api/curriculum/roadmap/:track', (req, res) => {
      try {
        const trackName = req.params.track.toLowerCase().replace('-', '_');
        const roadmap = this.generateRoadmap(trackName);
        
        res.json(roadmap);
      } catch (error) {
        res.status(500).json({ error: 'Failed to generate roadmap' });
      }
    });

    // Schedule validation
    this.app.post('/api/curriculum/validate-schedule', (req, res) => {
      try {
        const { courses, semester } = req.body;
        const validation = this.validateSchedule(courses, semester);
        
        res.json(validation);
      } catch (error) {
        res.status(500).json({ error: 'Failed to validate schedule' });
      }
    });

    // Elective recommendations
    this.app.get('/api/curriculum/electives/:track', (req, res) => {
      try {
        const trackName = req.params.track.toLowerCase().replace('-', '_');
        const recommendations = this.getElectiveRecommendations(trackName);
        
        res.json(recommendations);
      } catch (error) {
        res.status(500).json({ error: 'Failed to get elective recommendations' });
      }
    });

    // Search courses
    this.app.get('/api/curriculum/search', (req, res) => {
      try {
        const { q, track, credits } = req.query;
        let results = this.curriculumData.courses;
        
        // Filter by search query
        if (q) {
          const query = q.toLowerCase();
          results = results.filter(course => 
            course.code.toLowerCase().includes(query) ||
            course.title.toLowerCase().includes(query) ||
            course.description.toLowerCase().includes(query)
          );
        }
        
        // Filter by track
        if (track) {
          const trackData = this.curriculumData.tracks[track.toLowerCase().replace('-', '_')];
          if (trackData) {
            const trackCourses = [
              ...trackData.required_courses.map(c => c.code),
              ...trackData.elective_courses.map(c => c.code)
            ];
            results = results.filter(course => trackCourses.includes(course.code));
          }
        }
        
        // Filter by credits
        if (credits) {
          results = results.filter(course => course.credits === parseInt(credits));
        }
        
        res.json({
          query: { q, track, credits },
          results: results.slice(0, 50) // Limit results
        });
      } catch (error) {
        res.status(500).json({ error: 'Failed to search courses' });
      }
    });

    // Statistics
    this.app.get('/api/curriculum/statistics', (req, res) => {
      try {
        res.json(this.curriculumData.statistics);
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch statistics' });
      }
    });
  }

  getPrerequisiteChain(courseCode, visited = new Set()) {
    if (visited.has(courseCode)) return []; // Avoid cycles
    
    visited.add(courseCode);
    const prerequisites = this.curriculumData.prerequisiteMap[courseCode]?.prerequisites || [];
    
    const chain = [];
    prerequisites.forEach(prereq => {
      const course = this.curriculumData.courses.find(c => c.code === prereq);
      if (course) {
        chain.push({
          ...course,
          prerequisites: this.getPrerequisiteChain(prereq, visited)
        });
      }
    });
    
    return chain;
  }

  generateRoadmap(trackName) {
    const track = this.curriculumData.tracks[trackName];
    if (!track) return { error: 'Track not found' };
    
    const coreRequirements = this.curriculumData.knowledgeTree.branches.core_requirements.courses;
    const trackRequired = track.required_courses.map(c => c.code);
    const trackElectives = track.elective_courses.map(c => c.code);
    
    // Simple semester planning (would need more complex logic for real planning)
    const roadmap = {
      track: trackName,
      semesters: [
        { semester: 1, courses: coreRequirements.slice(0, 2) },
        { semester: 2, courses: coreRequirements.slice(2, 4) },
        { semester: 3, courses: [...coreRequirements.slice(4), ...trackRequired.slice(0, 1)] },
        { semester: 4, courses: trackRequired.slice(1, 3) },
        { semester: 5, courses: [...trackRequired.slice(3), ...trackElectives.slice(0, 1)] },
        { semester: 6, courses: trackElectives.slice(1, 3) }
      ]
    };
    
    return roadmap;
  }

  validateSchedule(courses, semester) {
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      recommendations: []
    };
    
    // Check prerequisites
    courses.forEach(courseCode => {
      const prerequisites = this.curriculumData.prerequisiteMap[courseCode]?.prerequisites || [];
      const missingPrereqs = prerequisites.filter(prereq => !courses.includes(prereq));
      
      if (missingPrereqs.length > 0) {
        validation.valid = false;
        validation.errors.push({
          course: courseCode,
          issue: 'Missing prerequisites',
          details: missingPrereqs
        });
      }
    });
    
    // Check credit load
    const totalCredits = courses.reduce((sum, courseCode) => {
      const course = this.curriculumData.courses.find(c => c.code === courseCode);
      return sum + (course?.credits || 0);
    }, 0);
    
    if (totalCredits > 18) {
      validation.warnings.push({
        issue: 'Heavy credit load',
        details: `${totalCredits} credits may be challenging`
      });
    }
    
    if (totalCredits < 12) {
      validation.warnings.push({
        issue: 'Light credit load',
        details: `${totalCredits} credits may not meet full-time requirements`
      });
    }
    
    return validation;
  }

  getElectiveRecommendations(trackName) {
    const track = this.curriculumData.tracks[trackName];
    if (!track) return { error: 'Track not found' };
    
    const recommendations = {
      track: trackName,
      required_electives: track.min_electives,
      options: track.elective_courses.map(course => ({
        ...course,
        prerequisites: this.curriculumData.prerequisiteMap[course.code]?.prerequisites || [],
        difficulty: this.estimateCourseDifficulty(course.code)
      }))
    };
    
    return recommendations;
  }

  estimateCourseDifficulty(courseCode) {
    // Simple heuristic based on course number
    const courseNumber = parseInt(courseCode.replace('CS ', ''));
    if (courseNumber < 20000) return 'beginner';
    if (courseNumber < 30000) return 'intermediate';
    if (courseNumber < 40000) return 'advanced';
    return 'expert';
  }

  async start() {
    await this.loadData();
    
    this.app.listen(this.port, () => {
      console.log(`🚀 Curriculum API Server running on port ${this.port}`);
      console.log(`📊 Loaded ${this.curriculumData.courses.length} courses`);
      console.log(`📚 Available tracks: ${Object.keys(this.curriculumData.tracks).join(', ')}`);
      console.log(`🌐 API documentation: http://localhost:${this.port}/api`);
    });
  }
}

// Start server if run directly
if (require.main === module) {
  const server = new CurriculumAPI();
  server.start().catch(console.error);
}

module.exports = CurriculumAPI;