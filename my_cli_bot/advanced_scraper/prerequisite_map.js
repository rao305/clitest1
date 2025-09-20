/**
 * Accurate Prerequisite Mapping from Official Purdue CS Flowchart
 * Updated with verified prerequisite chains and course relationships
 */

const prerequisiteMap = {
  // Core Courses (Required for all CS majors)
  'CS18000': { 
    code: 'CS 18000',
    title: 'Problem Solving and Object-Oriented Programming',
    credits: 4,
    prerequisites: [],
    corequisites: ['MA16100'], // Can be taken concurrently
    notes: 'Foundation course',
    category: 'core'
  },
  'CS18200': {
    code: 'CS 18200', 
    title: 'Foundations of Computer Science',
    credits: 3,
    prerequisites: ['CS18000', 'MA16100'],
    notes: 'Requires C or better in CS 18000',
    category: 'core'
  },
  'CS24000': {
    code: 'CS 24000',
    title: 'Programming in C',
    credits: 3,
    prerequisites: ['CS18000'],
    notes: 'Requires C or better in CS 18000',
    category: 'core'
  },
  'CS25000': {
    code: 'CS 25000',
    title: 'Computer Architecture',
    credits: 4,
    prerequisites: ['CS18200', 'CS24000'],
    notes: 'Requires C or better in both CS 18200 and CS 24000',
    category: 'core'
  },
  'CS25100': {
    code: 'CS 25100',
    title: 'Data Structures and Algorithms',
    credits: 3,
    prerequisites: ['CS18200', 'CS24000'],
    notes: 'Requires C or better in both CS 18200 and CS 24000',
    category: 'core'
  },
  'CS25200': {
    code: 'CS 25200',
    title: 'Systems Programming',
    credits: 4,
    prerequisites: ['CS25000', 'CS25100'],
    notes: 'Requires C or better in both CS 25000 and CS 25100',
    category: 'core'
  },
  'CS30700': {
    code: 'CS 30700',
    title: 'Software Engineering I',
    credits: 3,
    prerequisites: ['CS25100'],
    category: 'core'
  },

  // Math/Stats Prerequisites
  'MA16100': {
    code: 'MA 16100',
    title: 'Plane Analytic Geometry And Calculus I',
    credits: 5,
    prerequisites: [],
    notes: 'Calculus I - Required for CS minors',
    category: 'math'
  },
  'MA16200': {
    code: 'MA 16200',
    title: 'Plane Analytic Geometry And Calculus II',
    credits: 5,
    prerequisites: ['MA16100'],
    category: 'math'
  },
  'MA26100': {
    code: 'MA 26100',
    title: 'Multivariate Calculus',
    credits: 4,
    prerequisites: ['MA16200'],
    category: 'math'
  },
  'MA26500': {
    code: 'MA 26500',
    title: 'Linear Algebra',
    credits: 3,
    prerequisites: ['MA26100'],
    corequisites: ['MA26100'], // Can be taken concurrently
    category: 'math'
  },
  'STAT35000': {
    code: 'STAT 35000',
    title: 'Introduction to Statistics',
    credits: 3,
    prerequisites: ['MA16200'],
    category: 'math'
  },

  // Machine Intelligence Track Required
  'CS37300': {
    code: 'CS 37300',
    title: 'Data Mining and Machine Learning',
    credits: 3,
    prerequisites: ['CS25200', 'STAT35000'],
    trackRequired: ['machine_intelligence'],
    category: 'mi_track'
  },
  'CS38100': {
    code: 'CS 38100',
    title: 'Introduction to the Analysis of Algorithms',
    credits: 3,
    prerequisites: ['CS25200', 'MA26100'],
    trackRequired: ['machine_intelligence', 'software_engineering'],
    category: 'advanced'
  },

  // Software Engineering Track Required
  'CS35200': {
    code: 'CS 35200',
    title: 'Compilers: Principles and Practice',
    credits: 4,
    prerequisites: ['CS25200'],
    trackRequired: ['software_engineering'],
    category: 'se_track'
  },
  'CS35400': {
    code: 'CS 35400',
    title: 'Operating Systems',
    credits: 4,
    prerequisites: ['CS25200'],
    trackRequired: ['software_engineering'],
    category: 'se_track'
  },
  'CS40800': {
    code: 'CS 40800',
    title: 'Software Testing',
    credits: 3,
    prerequisites: ['CS25100'],
    trackRequired: ['software_engineering'],
    category: 'se_track'
  },

  // Additional Advanced Courses
  'CS31400': {
    code: 'CS 31400',
    title: 'Numerical Methods',
    credits: 3,
    prerequisites: ['MA26100', 'STAT35000'],
    prerequisiteType: 'either', // Either MA or STAT prerequisites
    notes: 'Requires MA/STAT prerequisites',
    category: 'elective'
  },
  'CS33400': {
    code: 'CS 33400',
    title: 'Discrete Computational Structures',
    credits: 3,
    prerequisites: ['MA26500'],
    notes: 'Requires MA prerequisites',
    category: 'elective'
  },
  'CS34800': {
    code: 'CS 34800',
    title: 'Information Systems',
    credits: 3,
    prerequisites: ['CS25100'],
    category: 'elective'
  },
  'CS35300': {
    code: 'CS 35300',
    title: 'Compilers: Back End',
    credits: 4,
    prerequisites: ['CS35200'],
    category: 'elective'
  },
  'CS35500': {
    code: 'CS 35500',
    title: 'Introduction to Cryptography',
    credits: 3,
    prerequisites: ['MA26500'],
    notes: 'Requires MA prerequisites',
    category: 'elective'
  },
  'CS40700': {
    code: 'CS 40700',
    title: 'Software Engineering II',
    credits: 3,
    prerequisites: ['CS30700'],
    category: 'elective'
  },
  'CS42200': {
    code: 'CS 42200',
    title: 'Computer Networks',
    credits: 3,
    prerequisites: ['CS35400'],
    corequisites: ['CS25200'], // Can be concurrent
    category: 'elective'
  },
  'CS42600': {
    code: 'CS 42600',
    title: 'Computer Security',
    credits: 3,
    prerequisites: ['CS35400'],
    category: 'elective'
  },
  'CS43400': {
    code: 'CS 43400',
    title: 'Programming Languages',
    credits: 3,
    prerequisites: ['CS33400'],
    category: 'elective'
  },
  'CS44800': {
    code: 'CS 44800',
    title: 'Introduction to Relational Database Systems',
    credits: 3,
    prerequisites: ['CS25100'],
    category: 'elective'
  },
  'CS45600': {
    code: 'CS 45600',
    title: 'Programming Languages',
    credits: 3,
    prerequisites: ['CS35200'],
    category: 'elective'
  },
  'CS47100': {
    code: 'CS 47100',
    title: 'Introduction to Artificial Intelligence',
    credits: 3,
    prerequisites: ['CS25100'],
    category: 'mi_track'
  },
  'CS47300': {
    code: 'CS 47300',
    title: 'Web Information Search and Management',
    credits: 3,
    prerequisites: ['CS25100'],
    category: 'mi_track'
  },
  'CS47800': {
    code: 'CS 47800',
    title: 'Introduction to Bioinformatics',
    credits: 3,
    prerequisites: ['CS18000'],
    notes: 'Requires additional prerequisites outside CS department',
    category: 'mi_track'
  },
  'CS48300': {
    code: 'CS 48300',
    title: 'Introduction to the Theory of Computation',
    credits: 3,
    prerequisites: ['CS38100'],
    category: 'elective'
  },
  'CS48900': {
    code: 'CS 48900',
    title: 'Embedded Systems',
    credits: 3,
    prerequisites: ['CS25200'],
    category: 'elective'
  },
  'CS49000': {
    code: 'CS 49000',
    title: 'Deep Learning',
    credits: 3,
    prerequisites: ['CS47100'],
    category: 'mi_track'
  },
  'CS42300': {
    code: 'CS 42300',
    title: 'Computer Graphics',
    credits: 3,
    prerequisites: ['CS25100'],
    category: 'elective'
  }
};

module.exports = prerequisiteMap;