// test-api-endpoints.js
const express = require('express');
const fs = require('fs').promises;
const path = require('path');

async function testAPI() {
  console.log('🧪 Testing API Endpoints...\n');
  
  try {
    // Load real curriculum data
    const dataPath = path.join(__dirname, '..', 'data', 'real_curriculum_data.json');
    const rawData = await fs.readFile(dataPath, 'utf8');
    const curriculumData = JSON.parse(rawData);
    
    const app = express();
    app.use(express.json());
    
    // Setup real data endpoints
    app.get('/api/curriculum/core', (req, res) => {
      res.json({ 
        courses: curriculumData.coreCourses,
        count: curriculumData.coreCourses.length
      });
    });
    
    app.get('/api/curriculum/tracks/:name', (req, res) => {
      const trackName = req.params.name;
      const track = curriculumData.tracks[trackName];
      
      if (track) {
        res.json({
          name: trackName,
          required: track.required,
          electives: track.electives,
          totalCourses: track.required.length + track.electives.length
        });
      } else {
        res.status(404).json({ error: 'Track not found' });
      }
    });
    
    app.get('/api/curriculum/course/:code', (req, res) => {
      const courseCode = req.params.code;
      const course = curriculumData.allCourses.find(c => c.code === courseCode);
      
      if (course) {
        res.json(course);
      } else {
        res.status(404).json({ error: 'Course not found' });
      }
    });
    
    app.get('/api/curriculum/prerequisites/:code', (req, res) => {
      const courseCode = req.params.code;
      const course = curriculumData.prerequisiteGraph.find(c => c.code === courseCode);
      
      if (course) {
        res.json({
          course: courseCode,
          prerequisites: course.prerequisites,
          dependents: course.dependents
        });
      } else {
        res.status(404).json({ error: 'Course not found' });
      }
    });
    
    // Start server
    const server = app.listen(3000);
    
    // Give server time to start
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Test endpoints
    const testResults = {
      passed: 0,
      failed: 0,
      total: 0
    };
    
    // Test 1: Core courses endpoint
    console.log('📝 Test 1: GET /api/curriculum/core');
    testResults.total++;
    
    try {
      const response = await fetch('http://localhost:3000/api/curriculum/core');
      const data = await response.json();
      
      if (response.ok && data.courses && data.courses.length > 0) {
        console.log(`✅ Retrieved ${data.count} core courses`);
        testResults.passed++;
      } else {
        console.log('❌ Failed to retrieve core courses');
        testResults.failed++;
      }
    } catch (error) {
      console.log('❌ Error:', error.message);
      testResults.failed++;
    }
    console.log('');
    
    // Test 2: Track endpoint
    console.log('📝 Test 2: GET /api/curriculum/tracks/machineIntelligence');
    testResults.total++;
    
    try {
      const response = await fetch('http://localhost:3000/api/curriculum/tracks/machineIntelligence');
      const data = await response.json();
      
      if (response.ok && data.name) {
        console.log(`✅ Track: ${data.name}`);
        console.log(`   Required: ${data.required.length} courses`);
        console.log(`   Electives: ${data.electives.length} courses`);
        testResults.passed++;
      } else {
        console.log('❌ Failed to retrieve track data');
        testResults.failed++;
      }
    } catch (error) {
      console.log('❌ Error:', error.message);
      testResults.failed++;
    }
    console.log('');
    
    // Test 3: Course endpoint
    console.log('📝 Test 3: GET /api/curriculum/course/CS 18000');
    testResults.total++;
    
    try {
      const response = await fetch('http://localhost:3000/api/curriculum/course/CS 18000');
      const data = await response.json();
      
      if (response.ok && data.code) {
        console.log(`✅ Course: ${data.code} - ${data.title}`);
        console.log(`   Credits: ${data.credits}`);
        console.log(`   Prerequisites: ${data.prerequisites.join(', ') || 'None'}`);
        testResults.passed++;
      } else {
        console.log('❌ Failed to retrieve course data');
        testResults.failed++;
      }
    } catch (error) {
      console.log('❌ Error:', error.message);
      testResults.failed++;
    }
    console.log('');
    
    // Test 4: Prerequisites endpoint
    console.log('📝 Test 4: GET /api/curriculum/prerequisites/CS 25100');
    testResults.total++;
    
    try {
      const response = await fetch('http://localhost:3000/api/curriculum/prerequisites/CS 25100');
      const data = await response.json();
      
      if (response.ok && data.course) {
        console.log(`✅ Course: ${data.course}`);
        console.log(`   Prerequisites: ${data.prerequisites.join(', ') || 'None'}`);
        console.log(`   Dependents: ${data.dependents.join(', ') || 'None'}`);
        testResults.passed++;
      } else {
        console.log('❌ Failed to retrieve prerequisites');
        testResults.failed++;
      }
    } catch (error) {
      console.log('❌ Error:', error.message);
      testResults.failed++;
    }
    console.log('');
    
    // Test 5: Invalid endpoint
    console.log('📝 Test 5: GET /api/curriculum/tracks/invalid_track');
    testResults.total++;
    
    try {
      const response = await fetch('http://localhost:3000/api/curriculum/tracks/invalid_track');
      
      if (response.status === 404) {
        console.log(`✅ Status: ${response.status} (Expected: 404)`);
        testResults.passed++;
      } else {
        console.log(`❌ Unexpected status: ${response.status}`);
        testResults.failed++;
      }
    } catch (error) {
      console.log('❌ Error:', error.message);
      testResults.failed++;
    }
    console.log('');
    
    // Close server
    server.close();
    
    // Test summary
    console.log(`📊 API Test Summary: ${testResults.passed}/${testResults.total} tests passed`);
    
    return testResults.passed === testResults.total;
    
  } catch (error) {
    console.error('❌ API Test Error:', error.message);
    return false;
  }
}

// Run API tests
if (require.main === module) {
  testAPI().then(success => {
    console.log(success ? '🎉 API endpoint test completed successfully!' : '❌ API endpoint test failed');
    process.exit(success ? 0 : 1);
  });
}

module.exports = testAPI;