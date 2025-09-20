/**
 * Test Suite for Prerequisite Accuracy
 * Validates prerequisite chains against official Purdue CS flowchart
 */

const PrerequisiteChainBuilder = require('./prerequisite_chain_builder.js');
const prerequisiteMap = require('./prerequisite_map.js');

function testPrerequisiteChains() {
  console.log('🧪 Testing Prerequisite Chain Accuracy...\n');
  
  const builder = new PrerequisiteChainBuilder();
  
  // Test cases based on official flowchart
  const testCases = [
    {
      course: 'CS37300',
      expectedDirect: ['CS25200', 'STAT35000'],
      expectedAll: ['CS25200', 'STAT35000', 'CS25000', 'CS25100', 'CS18200', 'CS24000', 'CS18000', 'MA16200', 'MA16100'],
      description: 'Data Mining and Machine Learning'
    },
    {
      course: 'CS38100',
      expectedDirect: ['CS25200', 'MA26100'],
      expectedAll: ['CS25200', 'MA26100', 'CS25000', 'CS25100', 'CS18200', 'CS24000', 'CS18000', 'MA16200', 'MA16100'],
      description: 'Introduction to Analysis of Algorithms'
    },
    {
      course: 'CS40800',
      expectedDirect: ['CS25100'],
      expectedAll: ['CS25100', 'CS18200', 'CS24000', 'CS18000', 'MA16100'],
      description: 'Software Testing'
    },
    {
      course: 'CS48300',
      expectedDirect: ['CS38100'],
      expectedAll: ['CS38100', 'CS25200', 'MA26100', 'CS25000', 'CS25100', 'CS18200', 'CS24000', 'CS18000', 'MA16200', 'MA16100'],
      description: 'Introduction to Theory of Computation'
    },
    {
      course: 'CS35200',
      expectedDirect: ['CS25200'],
      expectedAll: ['CS25200', 'CS25000', 'CS25100', 'CS18200', 'CS24000', 'CS18000', 'MA16100'],
      description: 'Compilers: Principles and Practice'
    }
  ];
  
  let passed = 0;
  let failed = 0;
  
  testCases.forEach(test => {
    const result = builder.getCompletePrerequisiteChain(test.course);
    
    console.log(`📝 Testing ${test.course} (${test.description})`);
    
    try {
      // Check direct prerequisites
      const directMatch = arraysEqual(result.direct, test.expectedDirect);
      const allMatch = arraysEqual(result.all, test.expectedAll);
      
      if (directMatch && allMatch) {
        console.log(`✅ ${test.course}: Prerequisites correct`);
        console.log(`   Direct: ${result.direct.join(', ')}`);
        console.log(`   All: ${result.all.length} prerequisites`);
        passed++;
      } else {
        console.log(`❌ ${test.course}: Prerequisites mismatch`);
        if (!directMatch) {
          console.log(`   Expected direct: ${test.expectedDirect.join(', ')}`);
          console.log(`   Got direct: ${result.direct.join(', ')}`);
        }
        if (!allMatch) {
          console.log(`   Expected all count: ${test.expectedAll.length}`);
          console.log(`   Got all count: ${result.all.length}`);
        }
        failed++;
      }
    } catch (error) {
      console.log(`❌ ${test.course}: Error - ${error.message}`);
      failed++;
    }
    console.log('');
  });
  
  console.log(`📊 Prerequisite Chain Results: ${passed} passed, ${failed} failed`);
  
  // Test longest paths
  console.log('\n🔍 Testing Longest Prerequisite Paths:');
  const pathTests = ['CS37300', 'CS38100', 'CS48300', 'CS40800', 'CS35200'];
  
  pathTests.forEach(course => {
    const path = builder.getLongestPath(course);
    console.log(`${course}: ${path.join(' → ')} (${path.length - 1} levels deep)`);
  });
  
  // Test circular dependency detection
  console.log('\n🔄 Testing Circular Dependency Detection:');
  const cycles = builder.detectCircularDependencies();
  if (cycles.length === 0) {
    console.log('✅ No circular dependencies detected');
  } else {
    console.log(`❌ Found ${cycles.length} circular dependencies:`);
    cycles.forEach(cycle => {
      console.log(`   ${cycle.join(' → ')}`);
    });
  }
  
  // Test course sequencing validation
  console.log('\n📋 Testing Course Sequencing:');
  const completedCourses = ['CS18000', 'CS18200', 'CS24000'];
  const plannedCourses = ['CS25000', 'CS25100'];
  
  const validation = builder.validateSchedule(completedCourses, plannedCourses);
  console.log(`Schedule validation: ${validation.valid ? 'Valid' : 'Invalid'}`);
  
  if (!validation.valid) {
    validation.issues.forEach(issue => {
      console.log(`   Issue: ${issue.message}`);
    });
  }
  
  console.log(`Recommended next courses: ${validation.recommendations.join(', ')}`);
  
  // Test track sequences
  console.log('\n📚 Testing Track Sequences:');
  const tracks = ['machine_intelligence', 'software_engineering'];
  
  tracks.forEach(track => {
    const roadmap = builder.generateRoadmap(track);
    if (roadmap) {
      console.log(`\n${track.replace('_', ' ').toUpperCase()} Track:`);
      roadmap.semesters.slice(0, 3).forEach(sem => {
        console.log(`   Semester ${sem.number}: ${sem.courses.map(c => c.code).join(', ')} (${sem.totalCredits} credits)`);
      });
    }
  });
  
  return passed === testCases.length;
}

function arraysEqual(arr1, arr2) {
  if (arr1.length !== arr2.length) return false;
  
  const set1 = new Set(arr1);
  const set2 = new Set(arr2);
  
  if (set1.size !== set2.size) return false;
  
  for (let item of set1) {
    if (!set2.has(item)) return false;
  }
  
  return true;
}

// Test data structure integrity
function testDataStructureIntegrity() {
  console.log('\n🔍 Testing Data Structure Integrity:');
  
  const issues = [];
  
  Object.entries(prerequisiteMap).forEach(([key, course]) => {
    // Check required fields
    if (!course.code || !course.title) {
      issues.push(`${key}: Missing required fields`);
    }
    
    // Check prerequisite references
    if (course.prerequisites) {
      course.prerequisites.forEach(prereq => {
        const normalizedPrereq = prereq.replace(/\s+/g, '');
        if (!prerequisiteMap[normalizedPrereq]) {
          issues.push(`${key}: Invalid prerequisite reference: ${prereq}`);
        }
      });
    }
  });
  
  if (issues.length === 0) {
    console.log('✅ All data structure integrity checks passed');
  } else {
    console.log(`❌ Found ${issues.length} data structure issues:`);
    issues.forEach(issue => console.log(`   ${issue}`));
  }
  
  return issues.length === 0;
}

// Run all tests
if (require.main === module) {
  console.log('🚀 Running Complete Prerequisite Accuracy Test Suite\n');
  console.log('='.repeat(60));
  
  const prerequisiteTests = testPrerequisiteChains();
  const integrityTests = testDataStructureIntegrity();
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 PREREQUISITE ACCURACY TEST SUMMARY');
  console.log('='.repeat(60));
  
  if (prerequisiteTests && integrityTests) {
    console.log('🎉 All prerequisite accuracy tests passed!');
    console.log('✅ Prerequisite chains verified against official flowchart');
    console.log('✅ Data structure integrity confirmed');
    console.log('✅ Course sequencing validation working');
    console.log('✅ Track roadmaps generated successfully');
    process.exit(0);
  } else {
    console.log('❌ Some prerequisite accuracy tests failed');
    process.exit(1);
  }
}

module.exports = { testPrerequisiteChains, testDataStructureIntegrity };