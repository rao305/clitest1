#!/usr/bin/env python3
"""
Update Knowledge Base with Correct CS Requirements
Fixes CS 38100 classification and adds accurate degree requirements
"""

import json
import os

def update_cs_knowledge_base():
    """Update knowledge base with correct CS degree requirements"""
    
    # Load existing knowledge graph
    kg_path = "data/cs_knowledge_graph.json"
    if not os.path.exists(kg_path):
        print(f"❌ Knowledge graph not found: {kg_path}")
        return
    
    with open(kg_path, 'r') as f:
        kg_data = json.load(f)
    
    print("🔧 Updating CS knowledge base with accurate requirements...")
    
    # Fix CS 38100 classification
    if "CS 38100" in kg_data["courses"]:
        kg_data["courses"]["CS 38100"]["course_type"] = "required_core"
        kg_data["courses"]["CS 38100"]["title"] = "Introduction to the Analysis of Algorithms"
        kg_data["courses"]["CS 38100"]["description"] = "Introduction to the Analysis of Algorithms - Required core course for CS degree"
        kg_data["courses"]["CS 38100"]["semester"] = "Spring 2nd Year"
        kg_data["courses"]["CS 38100"]["is_critical"] = True
        print("✅ Fixed CS 38100 classification: foundation → required_core")
    
    # Add accurate CS degree requirements structure
    kg_data["degree_requirements"] = {
        "cs_core_required": [
            "CS 18000",  # Problem Solving and Object-Oriented Programming
            "CS 18200",  # Foundations of Computer Science  
            "CS 24000",  # Programming in C
            "CS 25000",  # Computer Architecture
            "CS 25100",  # Data Structures and Algorithms
            "CS 25200",  # Systems Programming
            "CS 35100",  # Introduction to Software Engineering
            "CS 35200",  # Compilers
            "CS 38100"   # Introduction to the Analysis of Algorithms ⭐ REQUIRED CORE
        ],
        "math_science_required": [
            "MATH 16100",  # Calculus I
            "MATH 16200",  # Calculus II
            "MATH 26100",  # Multivariable Calculus
            "MATH 26500",  # Linear Algebra (or MA 35100)
            "STAT 35000",  # Elementary Statistics
            "PHYS 17200",  # Modern Mechanics
            "PHYS 27200"   # Electric & Magnetic Interactions
        ],
        "total_credits_required": 120,
        "cs_core_credits": 29,  # Updated to include CS 38100
        "track_credits_required": 12,
        "general_education_credits": 30,
        "science_credits": 8,
        "free_electives": 15
    }
    
    # Add Machine Intelligence track requirements (accurate)
    kg_data["tracks"]["Machine Intelligence"] = {
        "track_code": "MI",
        "description": "Focus on artificial intelligence, machine learning, and data science",
        "core_required": [
            "CS 37300",  # Data Mining and Machine Learning
            "CS 38100"   # Introduction to the Analysis of Algorithms
        ],
        "choose_one_ai": [
            {
                "code": "CS 47100",
                "title": "Introduction to Machine Learning",
                "recommended_for": "theoretical ML, research, graduate school"
            },
            {
                "code": "CS 47300", 
                "title": "Web Information Search & Management",
                "recommended_for": "web applications, industry, applied data mining"
            }
        ],
        "choose_one_probability": [
            {
                "code": "STAT 41600",
                "title": "Probability",
                "recommended_for": "theoretical foundations, research"
            },
            {
                "code": "MA 41600",
                "title": "Probability", 
                "recommended_for": "mathematical approach, pure theory"
            },
            {
                "code": "STAT 51200",
                "title": "Applied Regression Analysis",
                "recommended_for": "applied statistics, data analysis, industry"
            }
        ],
        "total_credits": 12,
        "prerequisites": {
            "CS 37300": ["CS 25100", "STAT 35000"],
            "CS 38100": ["CS 25100", "MATH 26500"],
            "CS 47100": ["CS 37300", "CS 38100"],
            "CS 47300": ["CS 25100", "CS 35100"],
            "STAT 41600": ["MATH 26100", "STAT 35000"],
            "MA 41600": ["MATH 26100"],
            "STAT 51200": ["STAT 35000"]
        }
    }
    
    # Update course classifications for better organization
    course_classifications = {
        # Foundation courses (first 2 years)
        "foundation": ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"],
        
        # Required core courses (must take for degree)
        "required_core": ["CS 35100", "CS 35200", "CS 38100"],
        
        # Track courses
        "track_mi": ["CS 37300", "CS 47100", "CS 47300"],
        "track_se": ["CS 30700", "CS 40800", "CS 41000"],
        
        # Math requirements
        "math_required": ["MATH 16100", "MATH 16200", "MATH 26100", "MATH 26500", "STAT 35000"],
        
        # Science requirements  
        "science_required": ["PHYS 17200", "PHYS 27200"]
    }
    
    # Update course types in the courses section
    for course_type, courses in course_classifications.items():
        for course_code in courses:
            if course_code in kg_data["courses"]:
                kg_data["courses"][course_code]["course_type"] = course_type
    
    # Add graduation timeline information
    kg_data["graduation_timelines"] = {
        "standard_4_year": {
            "total_semesters": 8,
            "credits_per_semester": 15,
            "description": "Standard 4-year graduation path"
        },
        "accelerated_3_5_year": {
            "total_semesters": 7,
            "credits_per_semester": 17.1,
            "description": "Accelerated graduation (possible with strong foundation)",
            "requirements": ["Strong math background", "18+ credits per semester", "Summer courses optional"]
        },
        "early_graduation_tips": [
            "Complete Calc I-III in first year",
            "Take 18+ credits per semester",
            "Use AP/transfer credits effectively", 
            "Plan track courses carefully",
            "Consider summer courses for lighter loads"
        ]
    }
    
    # Add CODO requirements (accurate)
    kg_data["codo_requirements"] = {
        "minimum_gpa": 3.2,
        "required_courses": [
            {
                "code": "MATH 16100",
                "title": "Calculus I", 
                "minimum_grade": "C"
            },
            {
                "code": "MATH 16200",
                "title": "Calculus II",
                "minimum_grade": "C" 
            },
            {
                "code": "CS 18000",
                "title": "Problem Solving and Object-Oriented Programming",
                "minimum_grade": "C"
            }
        ],
        "application_deadlines": {
            "fall_admission": "March 1",
            "spring_admission": "November 1"
        },
        "additional_requirements": [
            "Submit CODO application through myPurdue",
            "Meet with academic advisor",
            "Maximum 2 attempts at CS 18000",
            "Good academic standing"
        ],
        "tips": [
            "Take prerequisite courses seriously", 
            "Maintain strong GPA",
            "Get involved in CS activities",
            "Seek help early if struggling",
            "Consider tutoring/SI sessions"
        ]
    }
    
    # Save updated knowledge graph
    backup_path = f"{kg_path}.backup"
    os.rename(kg_path, backup_path)
    print(f"📁 Backup created: {backup_path}")
    
    with open(kg_path, 'w') as f:
        json.dump(kg_data, f, indent=2)
    
    print("✅ Knowledge base updated successfully!")
    print("\n📊 Updates made:")
    print("   • CS 38100 correctly classified as 'required_core'")
    print("   • Added accurate MI track requirements with choices")
    print("   • Updated degree requirements structure")
    print("   • Added graduation timeline options")
    print("   • Added accurate CODO requirements")
    print("   • Organized course classifications")
    
    # Update comprehensive data as well
    update_comprehensive_data()

def update_comprehensive_data():
    """Update comprehensive data file"""
    comprehensive_path = "data/comprehensive_purdue_cs_data.json"
    
    if os.path.exists(comprehensive_path):
        with open(comprehensive_path, 'r') as f:
            comp_data = json.load(f)
        
        # Update CS 38100 in comprehensive data
        if "CS 38100" in comp_data.get("courses", {}):
            comp_data["courses"]["CS 38100"]["title"] = "Introduction to the Analysis of Algorithms"
            comp_data["courses"]["CS 38100"]["course_type"] = "required_core"
            comp_data["courses"]["CS 38100"]["credits"] = 3
        
        # Add MI track structure
        comp_data["tracks"]["Machine Intelligence"] = {
            "description": "Focus on AI, ML, and data science",
            "core_required": ["CS 37300", "CS 38100"],
            "choose_one_ai": ["CS 47100", "CS 47300"],
            "choose_one_stats": ["STAT 41600", "MA 41600", "STAT 51200"],
            "total_credits": 12
        }
        
        with open(comprehensive_path, 'w') as f:
            json.dump(comp_data, f, indent=2)
        
        print("✅ Comprehensive data updated as well!")

def main():
    """Main function"""
    print("🔧 Updating Purdue CS Knowledge Base")
    print("=" * 50)
    update_cs_knowledge_base()
    print("\n✅ All updates completed!")

if __name__ == "__main__":
    main()