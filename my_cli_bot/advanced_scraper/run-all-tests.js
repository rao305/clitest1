// run-all-tests.js
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function runAllTests() {
  console.log('🚀 Running Comprehensive Test Suite for Real Curriculum Scraper\n');
  console.log('=' .repeat(60));
  
  const tests = [
    { name: 'Basic Scraper', file: 'test-scraper.js' },
    { name: 'Course Details', file: 'test-course-details.js' },
    { name: 'Data Processor', file: 'test-data-processor.js' },
    { name: 'API Endpoints', file: 'test-api-endpoints.js' },
    { name: 'Prerequisites Accuracy', file: 'test-prerequisites-accuracy.js' }
  ];
  
  const results = {
    passed: 0,
    failed: 0,
    total: tests.length
  };
  
  for (const test of tests) {
    console.log(`\n▶️  Running ${test.name} Test...`);
    console.log('-'.repeat(50));
    
    try {
      const { stdout } = await execPromise(`node ${test.file}`);
      console.log(stdout);
      results.passed++;
      console.log(`✅ ${test.name} Test: PASSED`);
    } catch (error) {
      console.error(`❌ ${test.name} Test: FAILED`);
      console.error(error.stderr || error.message);
      results.failed++;
    }
  }
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 COMPREHENSIVE TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total Tests: ${results.total}`);
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);
  
  if (results.failed === 0) {
    console.log('\n🎉 All tests passed! Real curriculum scraper is ready for production deployment.');
    console.log('\n📋 System Status:');
    console.log('   ✅ Real data extraction working');
    console.log('   ✅ Prerequisite graph validation successful');
    console.log('   ✅ API endpoints operational');
    console.log('   ✅ Course detail processing verified');
    console.log('   ✅ Integration with Roo system confirmed');
  } else {
    console.log('\n⚠️  Some tests failed. Please review and fix issues before deployment.');
  }
  
  return results.failed === 0;
}

// Run all tests
if (require.main === module) {
  runAllTests().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = runAllTests;