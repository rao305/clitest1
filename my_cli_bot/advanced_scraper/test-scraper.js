// test-scraper.js
const WorkingPurdueCScraper = require('./working_scraper.js');

async function testBasicScraping() {
  console.log('🧪 Testing Basic Scraper...\n');
  
  try {
    const scraper = new WorkingPurdueCScraper();
    
    // Test 1: Basic scraper initialization
    console.log('📝 Test 1: Scraper initialization...');
    console.log('✅ Scraper initialized successfully\n');
    
    // Test 2: Process all data
    console.log('📝 Test 2: Processing real curriculum data...');
    const data = await scraper.processAllData();
    
    console.log(`✅ Found ${data.allCourses.length} total courses`);
    console.log(`✅ Found ${data.coreCourses.length} core courses`);
    console.log(`✅ Found ${data.tracks.machineIntelligence.required.length} MI required courses`);
    console.log(`✅ Found ${data.tracks.machineIntelligence.electives.length} MI elective courses`);
    console.log(`✅ Found ${data.tracks.softwareEngineering.electives.length} SE elective courses\n`);
    
    // Test 3: Validate prerequisite structure
    console.log('📝 Test 3: Validating prerequisite structure...');
    const prerequisiteGraph = data.prerequisiteGraph;
    const coursesWithPrereqs = prerequisiteGraph.filter(course => course.prerequisites.length > 0);
    
    console.log(`✅ Found ${coursesWithPrereqs.length} courses with prerequisites`);
    console.log('Sample prerequisite chains:');
    coursesWithPrereqs.slice(0, 3).forEach(course => {
      console.log(`   ${course.code}: ${course.prerequisites.join(', ')}`);
    });
    console.log('');
    
    // Test 4: Data integrity checks
    console.log('📝 Test 4: Data integrity checks...');
    const invalidCourses = data.allCourses.filter(course => 
      !course.code || !course.title || !course.credits || course.credits <= 0
    );
    
    if (invalidCourses.length === 0) {
      console.log('✅ All courses have valid data structure');
    } else {
      console.log(`❌ Found ${invalidCourses.length} courses with invalid data`);
    }
    
    console.log(`✅ Data source: ${data.source}`);
    console.log(`✅ Timestamp: ${data.timestamp}`);
    console.log(`✅ Errors: ${data.errors.length}`);
    
    return true;
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    return false;
  }
}

// Run the test
if (require.main === module) {
  testBasicScraping().then(success => {
    console.log(success ? '🎉 Basic scraper test completed successfully!' : '❌ Basic scraper test failed');
    process.exit(success ? 0 : 1);
  });
}

module.exports = testBasicScraping;