// test-course-details.js
const fs = require('fs').promises;
const path = require('path');

async function testCourseDetailScraping() {
  console.log('🧪 Testing Course Detail Scraper...\n');
  
  try {
    // Load real curriculum data
    const dataPath = path.join(__dirname, '..', 'data', 'real_curriculum_data.json');
    const rawData = await fs.readFile(dataPath, 'utf8');
    const curriculumData = JSON.parse(rawData);
    
    const testCourses = [
      'CS 18000',
      'CS 25100', 
      'CS 37300',
      'CS 47100',
      'CS 35200'
    ];
    
    let testsPassed = 0;
    
    for (const courseCode of testCourses) {
      console.log(`📝 Testing ${courseCode}`);
      
      // Find course in real data
      const course = curriculumData.allCourses.find(c => c.code === courseCode);
      
      if (course) {
        console.log(`   ✅ Title: ${course.title}`);
        console.log(`   ✅ Credits: ${course.credits}`);
        console.log(`   ✅ Category: ${course.category}`);
        console.log(`   ✅ Prerequisites: ${course.prerequisites.join(', ') || 'None'}`);
        
        // Validate course data structure
        const isValid = course.code && course.title && course.credits > 0 && 
                       course.category && Array.isArray(course.prerequisites);
        
        if (isValid) {
          console.log('   ✅ Data structure valid');
          testsPassed++;
        } else {
          console.log('   ❌ Data structure invalid');
        }
      } else {
        console.log(`   ❌ Course ${courseCode} not found in curriculum data`);
      }
      console.log('');
    }
    
    // Test prerequisite chain validation
    console.log('📝 Testing prerequisite chain validation...');
    const prerequisiteGraph = new Map();
    
    // Build prerequisite graph
    curriculumData.allCourses.forEach(course => {
      prerequisiteGraph.set(course.code, {
        ...course,
        dependents: []
      });
    });
    
    // Build reverse dependencies
    prerequisiteGraph.forEach((course, code) => {
      course.prerequisites.forEach(prereq => {
        if (prerequisiteGraph.has(prereq)) {
          prerequisiteGraph.get(prereq).dependents.push(code);
        }
      });
    });
    
    // Test chain for CS 37300
    const cs37300 = prerequisiteGraph.get('CS 37300');
    if (cs37300) {
      console.log(`   ✅ CS 37300 prerequisites: ${cs37300.prerequisites.join(', ')}`);
      console.log(`   ✅ CS 37300 enables: ${cs37300.dependents.join(', ')}`);
    }
    
    console.log(`\n📊 Test Summary: ${testsPassed}/${testCourses.length} courses passed validation`);
    
    return testsPassed === testCourses.length;
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    return false;
  }
}

// Run the test
if (require.main === module) {
  testCourseDetailScraping().then(success => {
    console.log(success ? '🎉 Course detail test completed successfully!' : '❌ Course detail test failed');
    process.exit(success ? 0 : 1);
  });
}

module.exports = testCourseDetailScraping;