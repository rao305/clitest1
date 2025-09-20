/**
 * Prerequisite Chain Builder for Accurate Course Sequencing
 * Processes prerequisite relationships and validates course sequences
 */

const prerequisiteMap = require('./prerequisite_map.js');

class PrerequisiteChainBuilder {
  constructor(customMap = null) {
    this.map = customMap || prerequisiteMap;
    this.cache = new Map();
  }

  /**
   * Get complete prerequisite chain for a course
   * @param {string} courseCode - Course code (e.g., 'CS37300')
   * @param {Set} visited - Set of already visited courses to prevent cycles
   * @returns {Object} - Complete prerequisite information
   */
  getCompletePrerequisiteChain(courseCode, visited = new Set()) {
    const normalizedCode = this.normalizeCourseCode(courseCode);
    
    if (this.cache.has(normalizedCode)) {
      return this.cache.get(normalizedCode);
    }

    if (visited.has(normalizedCode)) {
      return { direct: [], all: [], chain: [] };
    }

    visited.add(normalizedCode);
    const course = this.map[normalizedCode];
    
    if (!course) {
      return { direct: [], all: [], chain: [] };
    }

    const direct = course.prerequisites || [];
    let all = [...direct];
    const chains = [];

    // Recursively get prerequisites
    direct.forEach(prereq => {
      const prereqNormalized = this.normalizeCourseCode(prereq);
      const prereqData = this.getCompletePrerequisiteChain(prereqNormalized, new Set(visited));
      all = [...all, ...prereqData.all];
      
      // Build chain paths
      if (prereqData.chain.length === 0) {
        chains.push([prereq]);
      } else {
        prereqData.chain.forEach(chain => {
          chains.push([prereq, ...chain]);
        });
      }
    });

    // Remove duplicates while preserving order
    all = [...new Set(all)];

    const result = { direct, all, chain: chains };
    this.cache.set(normalizedCode, result);
    return result;
  }

  /**
   * Get the longest prerequisite path for a course
   * @param {string} courseCode - Course code
   * @returns {Array} - Longest prerequisite path
   */
  getLongestPath(courseCode) {
    const data = this.getCompletePrerequisiteChain(courseCode);
    let longest = [];
    
    data.chain.forEach(chain => {
      if (chain.length > longest.length) {
        longest = chain;
      }
    });

    return [courseCode, ...longest.reverse()];
  }

  /**
   * Check if a course can be taken given completed courses
   * @param {string} courseCode - Course to check
   * @param {Array} completedCourses - List of completed courses
   * @returns {boolean} - Whether the course can be taken
   */
  canTakeCourse(courseCode, completedCourses) {
    const normalizedCode = this.normalizeCourseCode(courseCode);
    const course = this.map[normalizedCode];
    
    if (!course) return false;

    const completed = new Set(completedCourses.map(c => this.normalizeCourseCode(c)));
    
    // Check prerequisites
    if (course.prerequisiteType === 'either') {
      // For either/or prerequisites, at least one must be completed
      return course.prerequisites.some(prereq => 
        completed.has(this.normalizeCourseCode(prereq))
      );
    } else {
      // All prerequisites must be completed
      return course.prerequisites.every(prereq => 
        completed.has(this.normalizeCourseCode(prereq))
      );
    }
  }

  /**
   * Generate a valid course sequence for a track
   * @param {string} trackName - Track name ('machine_intelligence' or 'software_engineering')
   * @returns {Object} - Track sequence information
   */
  generateTrackSequence(trackName) {
    const sequences = {
      machine_intelligence: {
        math: ['MA16100', 'MA16200', 'MA26100', 'STAT35000'],
        core: ['CS18000', 'CS18200', 'CS24000', 'CS25000', 'CS25100', 'CS25200', 'CS30700'],
        required: ['CS37300', 'CS38100'],
        suggestedElectives: ['CS34800', 'CS44800', 'CS47100', 'CS47300', 'CS48300', 'CS49000']
      },
      software_engineering: {
        math: ['MA16100', 'MA16200', 'MA26100'],
        core: ['CS18000', 'CS18200', 'CS24000', 'CS25000', 'CS25100', 'CS25200', 'CS30700'],
        required: ['CS35200', 'CS35400', 'CS38100', 'CS40800'],
        suggestedElectives: ['CS35300', 'CS34800', 'CS44800', 'CS45600', 'CS42200', 'CS42600']
      }
    };

    return sequences[trackName] || null;
  }

  /**
   * Validate a course schedule against prerequisites
   * @param {Array} completedCourses - Already completed courses
   * @param {Array} plannedCourses - Courses planned to take
   * @returns {Object} - Validation results
   */
  validateSchedule(completedCourses, plannedCourses) {
    const validation = {
      valid: true,
      issues: [],
      recommendations: []
    };

    plannedCourses.forEach(courseCode => {
      if (!this.canTakeCourse(courseCode, completedCourses)) {
        validation.valid = false;
        const normalizedCode = this.normalizeCourseCode(courseCode);
        const course = this.map[normalizedCode];
        
        if (course) {
          const missing = course.prerequisites.filter(p => 
            !completedCourses.includes(p) && !completedCourses.includes(this.normalizeCourseCode(p))
          );
          
          validation.issues.push({
            course: courseCode,
            missingPrerequisites: missing,
            message: `Cannot take ${courseCode} without completing: ${missing.join(', ')}`
          });
        }
      }
    });

    // Generate recommendations for available courses
    const allCourses = Object.keys(this.map);
    const available = allCourses.filter(courseCode => 
      this.canTakeCourse(courseCode, completedCourses) &&
      !completedCourses.includes(courseCode) &&
      !completedCourses.includes(this.denormalizeCourseCode(courseCode)) &&
      !plannedCourses.includes(courseCode) &&
      !plannedCourses.includes(this.denormalizeCourseCode(courseCode))
    );

    validation.recommendations = available.slice(0, 5).map(code => this.denormalizeCourseCode(code));

    return validation;
  }

  /**
   * Generate a semester-by-semester roadmap for a track
   * @param {string} trackName - Track name
   * @returns {Object} - Semester roadmap
   */
  generateRoadmap(trackName) {
    const sequence = this.generateTrackSequence(trackName);
    if (!sequence) {
      return null;
    }

    const roadmap = {
      track: trackName,
      semesters: []
    };

    const allCourses = [...sequence.math, ...sequence.core, ...sequence.required];
    const completed = new Set();

    // Simulate 8 semesters
    for (let sem = 1; sem <= 8; sem++) {
      const semesterCourses = [];
      const available = allCourses.filter(courseCode => {
        const normalizedCode = this.normalizeCourseCode(courseCode);
        return !completed.has(normalizedCode) &&
               this.canTakeCourse(courseCode, [...completed]);
      });

      // Take up to 4 courses per semester
      available.slice(0, 4).forEach(courseCode => {
        const normalizedCode = this.normalizeCourseCode(courseCode);
        const course = this.map[normalizedCode];
        
        if (course) {
          semesterCourses.push({
            code: course.code,
            title: course.title,
            credits: course.credits || 3,
            category: course.category
          });
          completed.add(normalizedCode);
        }
      });

      if (semesterCourses.length > 0) {
        roadmap.semesters.push({
          number: sem,
          courses: semesterCourses,
          totalCredits: semesterCourses.reduce((sum, c) => sum + c.credits, 0)
        });
      }
    }

    return roadmap;
  }

  /**
   * Normalize course code for consistent lookup
   * @param {string} courseCode - Course code
   * @returns {string} - Normalized course code
   */
  normalizeCourseCode(courseCode) {
    return courseCode.replace(/\s+/g, '').toUpperCase();
  }

  /**
   * Denormalize course code for display
   * @param {string} normalizedCode - Normalized course code
   * @returns {string} - Display-friendly course code
   */
  denormalizeCourseCode(normalizedCode) {
    const course = this.map[normalizedCode];
    return course ? course.code : normalizedCode;
  }

  /**
   * Get all courses for a specific track
   * @param {string} trackName - Track name
   * @returns {Array} - Array of course objects
   */
  getTrackCourses(trackName) {
    return Object.values(this.map).filter(course => 
      course.trackRequired && course.trackRequired.includes(trackName)
    );
  }

  /**
   * Detect circular dependencies in prerequisite chains
   * @returns {Array} - Array of circular dependency chains
   */
  detectCircularDependencies() {
    const visited = new Set();
    const recursionStack = new Set();
    const cycles = [];

    const dfs = (courseCode, path = []) => {
      if (recursionStack.has(courseCode)) {
        const cycleStart = path.indexOf(courseCode);
        cycles.push(path.slice(cycleStart).concat(courseCode));
        return;
      }

      if (visited.has(courseCode)) {
        return;
      }

      visited.add(courseCode);
      recursionStack.add(courseCode);

      const course = this.map[courseCode];
      if (course && course.prerequisites) {
        course.prerequisites.forEach(prereq => {
          const normalizedPrereq = this.normalizeCourseCode(prereq);
          dfs(normalizedPrereq, [...path, courseCode]);
        });
      }

      recursionStack.delete(courseCode);
    };

    Object.keys(this.map).forEach(courseCode => {
      if (!visited.has(courseCode)) {
        dfs(courseCode);
      }
    });

    return cycles;
  }
}

module.exports = PrerequisiteChainBuilder;