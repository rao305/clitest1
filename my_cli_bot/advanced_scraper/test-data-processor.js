// test-data-processor.js
const fs = require('fs').promises;
const path = require('path');

class DataProcessorTest {
  static async testPrerequisiteGraph() {
    console.log('🧪 Testing Prerequisite Graph Builder...\n');
    
    try {
      // Load real curriculum data
      const dataPath = path.join(__dirname, '..', 'data', 'real_curriculum_data.json');
      const rawData = await fs.readFile(dataPath, 'utf8');
      const curriculumData = JSON.parse(rawData);
      
      // Build graph from real data
      const graph = new Map();
      curriculumData.allCourses.forEach(course => {
        graph.set(course.code, {
          ...course,
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
      
      // Test results
      console.log('📊 Prerequisite Graph Analysis:');
      console.log(`   Total courses: ${graph.size}`);
      
      const coursesWithPrereqs = Array.from(graph.values()).filter(c => c.prerequisites.length > 0);
      const coursesWithDependents = Array.from(graph.values()).filter(c => c.dependents.length > 0);
      
      console.log(`   Courses with prerequisites: ${coursesWithPrereqs.length}`);
      console.log(`   Courses with dependents: ${coursesWithDependents.length}`);
      
      // Show sample chains
      console.log('\n📝 Sample Prerequisite Chains:');
      const sampleCourses = ['CS 24000', 'CS 25100', 'CS 35200'];
      
      sampleCourses.forEach(code => {
        const course = graph.get(code);
        if (course) {
          console.log(`\n${code} (${course.title}):`);
          console.log(`  Prerequisites: ${course.prerequisites.join(', ') || 'None'}`);
          console.log(`  Required for: ${course.dependents.join(', ') || 'None'}`);
        }
      });
      
      // Test path finding
      console.log('\n📝 Test: Find all prerequisites for CS 37300');
      const allPrereqs = this.findAllPrerequisites('CS 37300', graph);
      console.log(`✅ Result: ${Array.from(allPrereqs).join(' → ')}`);
      
      // Test circular dependency detection
      console.log('\n📝 Test: Circular dependency detection');
      const hasCircular = this.detectCircularDependencies(graph);
      console.log(`✅ Circular dependencies: ${hasCircular ? 'Found' : 'None'}`);
      
      // Test course sequencing
      console.log('\n📝 Test: Course sequencing validation');
      const sequenceValid = this.validateCourseSequencing(graph);
      console.log(`✅ Course sequencing: ${sequenceValid ? 'Valid' : 'Invalid'}`);
      
      return true;
      
    } catch (error) {
      console.error('❌ Error:', error.message);
      return false;
    }
  }
  
  static findAllPrerequisites(courseCode, graph, visited = new Set()) {
    const course = graph.get(courseCode);
    if (!course) return visited;
    
    course.prerequisites.forEach(prereq => {
      if (!visited.has(prereq)) {
        visited.add(prereq);
        this.findAllPrerequisites(prereq, graph, visited);
      }
    });
    
    return visited;
  }
  
  static detectCircularDependencies(graph) {
    const visited = new Set();
    const recursionStack = new Set();
    
    for (const [code] of graph) {
      if (this.hasCircularDependency(code, graph, visited, recursionStack)) {
        return true;
      }
    }
    
    return false;
  }
  
  static hasCircularDependency(courseCode, graph, visited, recursionStack) {
    if (recursionStack.has(courseCode)) {
      return true;
    }
    
    if (visited.has(courseCode)) {
      return false;
    }
    
    visited.add(courseCode);
    recursionStack.add(courseCode);
    
    const course = graph.get(courseCode);
    if (course) {
      for (const prereq of course.prerequisites) {
        if (this.hasCircularDependency(prereq, graph, visited, recursionStack)) {
          return true;
        }
      }
    }
    
    recursionStack.delete(courseCode);
    return false;
  }
  
  static validateCourseSequencing(graph) {
    // Check if all prerequisites exist in the graph
    for (const [code, course] of graph) {
      for (const prereq of course.prerequisites) {
        if (!graph.has(prereq)) {
          console.log(`   ❌ Missing prerequisite: ${prereq} for ${code}`);
          return false;
        }
      }
    }
    
    return true;
  }
}

// Run the test
if (require.main === module) {
  DataProcessorTest.testPrerequisiteGraph().then(success => {
    console.log(success ? '🎉 Data processor test completed successfully!' : '❌ Data processor test failed');
    process.exit(success ? 0 : 1);
  });
}

module.exports = DataProcessorTest;