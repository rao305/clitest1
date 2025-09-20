# ds_prereq_chain.py

from collections import defaultdict

# -----------------------------------------------------------------------------
# Prerequisite graph for Data Science major (Fall 2024)
#
# For each course key, the list is the courses that must be completed
# (or concurrently taken, where noted with a comment) with C or better.
# -----------------------------------------------------------------------------
prereqs = {
    # --- Core foundation ---
    'MA 161': [],                    # Calculus I
    'MA 162': ['MA 161'],            # Calculus II
    'MA 261': ['MA 162'],            # Calc III
    'MA 351': ['MA 162'],            # Linear Algebra (DS uses MA 35100, mapped to 351)
    'STAT 355': [],                  # Statistics I
    'STAT 416': ['MA 261'],          # Probability (requires multivariate calc)
    'STAT 417': ['STAT 416'],        # Statistical Theory

    # --- CS foundation ---
    'CS 180': [],                    # Problem Solving & OOP
    'CS 182': ['CS 180', 'MA 161'],  # Foundations; requires Calc I (C or better)
    'CS/STAT 242': ['MA 161'],       # Intro to Data Science (may be concurrent with MA 161)
    'CS 253': ['CS/STAT 242', 'CS 182'],  # Data Structures for DS/AI
    'CS 373': ['CS 253', 'STAT 355'], # Data Mining & Machine Learning
    'CS 440': ['CS 373'],            # Large Scale Data Analytics

    # --- Support courses ---
    'CS 38003': ['CS 182'],          # Python Programming
    'COM 217': [],                   # Science Writing (may require 60+ credits)

    # --- CS electives (DS-focus) ---
    'CS 311': ['CS 253'],            # Competitive Programming II
    'CS 411': ['CS 311'],            # Competitive Programming III  
    'CS 314': ['CS 253'],            # Numerical Methods
    'CS 355': ['CS 253'],            # Introduction to Cryptography
    'CS 439': ['CS 253'],            # Data Visualization
    'CS 458': ['CS 253'],            # Introduction to Robotics
    'CS 471': ['CS 253'],            # Introduction to AI
    'CS 473': ['CS 253'],            # Web Information Search
    'CS 475': ['CS 253'],            # Human-Computer Interaction
    'CS 307': ['CS 182'],            # Software Engineering I
    'CS 408': ['CS 307'],            # Software Testing
    'CS 348': ['CS 253'],            # Information Systems
    'CS 448': ['CS 253'],            # Database Systems
    'CS 381': ['CS 253'],            # Algorithm Analysis
    'CS 483': ['CS 253'],            # Theory of Computation

    # --- STAT electives (DS-focus) ---
    'MA 432': ['STAT 416'],          # Elementary Stochastic Processes
    'STAT 420': ['STAT 355'],        # Time Series Analysis
    'STAT 506': ['STAT 355'],        # Statistical Programming
    'STAT 512': ['STAT 416'],        # Applied Regression
    'STAT 513': ['STAT 416'],        # Quality Control
    'STAT 514': ['STAT 416'],        # Design of Experiments
    'STAT 522': ['STAT 416'],        # Sampling & Survey Techniques
    'STAT 525': ['STAT 416'],        # Intermediate Statistical Methodology
}

def get_full_prereq_chain(course, _seen=None):
    """
    Recursively compute the full set of prerequisites for a given course.
    Returns a set of all courses that must be taken before 'course'.
    """
    if _seen is None:
        _seen = set()
    for pre in prereqs.get(course, []):
        if pre not in _seen:
            _seen.add(pre)
            get_full_prereq_chain(pre, _seen)
    return _seen

def check_prerequisites_met(course, completed_courses):
    """
    Check if all prerequisites for a course have been completed.
    Returns True if all prereqs are met, False otherwise.
    """
    required_prereqs = prereqs.get(course, [])
    return all(prereq in completed_courses for prereq in required_prereqs)

def get_next_available_courses(completed_courses, all_courses=None):
    """
    Get list of courses that can be taken next given completed courses.
    """
    if all_courses is None:
        all_courses = list(prereqs.keys())
    
    available = []
    for course in all_courses:
        if course not in completed_courses and check_prerequisites_met(course, completed_courses):
            available.append(course)
    
    return sorted(available)

def get_ds_graduation_requirements():
    """
    Return the core Data Science major requirements organized by category.
    """
    return {
        'cs_core': ['CS 180', 'CS 182', 'CS/STAT 242', 'CS 253', 'CS 373', 'CS 440'],
        'math_requirements': ['MA 161', 'MA 162', 'MA 261', 'MA 351'],
        'stats_requirements': ['STAT 355', 'STAT 416', 'STAT 417'],
        'support_courses': ['CS 38003', 'COM 217'],
        'cs_electives_needed': 2,  # Choose 2 from approved CS electives
        'stats_electives_needed': 1,  # Choose 1 from approved stats electives
        'ethics_courses_needed': 1,  # Choose 1 from approved ethics courses
        'capstone_needed': 1,  # Choose 1 capstone experience
        'total_credits_required': 120
    }

def validate_ds_degree_plan(completed_courses):
    """
    Validate if a set of completed courses meets DS graduation requirements.
    Returns dict with validation results.
    """
    requirements = get_ds_graduation_requirements()
    results = {
        'cs_core_met': 0,
        'math_requirements_met': 0,
        'stats_requirements_met': 0,
        'cs_electives_met': 0,
        'stats_electives_met': 0,
        'missing_courses': [],
        'graduation_eligible': False
    }
    
    # Check core requirements
    for course in requirements['cs_core']:
        if course in completed_courses:
            results['cs_core_met'] += 1
        else:
            results['missing_courses'].append(course)
    
    for course in requirements['math_requirements']:
        if course in completed_courses:
            results['math_requirements_met'] += 1
        else:
            results['missing_courses'].append(course)
    
    for course in requirements['stats_requirements']:
        if course in completed_courses:
            results['stats_requirements_met'] += 1
        else:
            results['missing_courses'].append(course)
    
    # Check if graduation requirements are met
    cs_core_complete = results['cs_core_met'] == len(requirements['cs_core'])
    math_complete = results['math_requirements_met'] == len(requirements['math_requirements'])
    stats_complete = results['stats_requirements_met'] == len(requirements['stats_requirements'])
    
    results['graduation_eligible'] = cs_core_complete and math_complete and stats_complete
    
    return results

if __name__ == '__main__':
    # Example usage:
    target = 'CS 373'
    chain = get_full_prereq_chain(target)
    print(f"To take {target}, you must first complete: {sorted(chain)}")
    
    # Test prerequisite checking
    completed = {'CS 180', 'CS 182', 'MA 161', 'MA 162', 'STAT 355', 'CS/STAT 242', 'CS 253'}
    next_courses = get_next_available_courses(completed)
    print(f"With completed courses {completed}, you can take: {next_courses}")
    
    # Test degree validation
    validation = validate_ds_degree_plan(completed)
    print(f"Degree validation: {validation}")