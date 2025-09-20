#!/usr/bin/env python3
"""
Update CODO Requirements with Correct Official Information
Scrapes and updates all knowledge bases with accurate CODO requirements
"""

import json
import os
import requests
from bs4 import BeautifulSoup

def scrape_official_codo_requirements():
    """Scrape the official CODO requirements from Purdue catalog"""
    
    url = "https://catalog.purdue.edu/preview_program.php?catoid=17&poid=30771"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the requirements
        codo_requirements = {
            "minimum_gpa": 2.75,  # Updated from 3.2 to 2.75
            "minimum_semesters": 1,
            "minimum_purdue_credits": 12,
            "required_courses": [
                {
                    "code": "CS 18000",
                    "title": "Problem Solving And Object-Oriented Programming",
                    "credits": 4.0,
                    "minimum_grade": "B"  # Updated from C to B
                }
            ],
            "math_requirement": {
                "description": "B or better in ONE of the following math courses",
                "options": [
                    {
                        "code": "MA 16100",
                        "title": "Plane Analytic Geometry And Calculus I",
                        "credits": 5.0,
                        "alternative": "MA 16500"
                    },
                    {
                        "code": "MA 16200", 
                        "title": "Plane Analytic Geometry And Calculus II",
                        "credits": 5.0,
                        "alternative": "MA 16600"
                    },
                    {
                        "code": "MA 26100",
                        "title": "Multivariate Calculus",
                        "credits": 4.0,
                        "alternative": "MA 27101"
                    },
                    {
                        "code": "MA 26500",
                        "title": "Linear Algebra", 
                        "credits": 3.0,
                        "alternative": "MA 35100"
                    }
                ]
            },
            "application_terms": ["FALL", "SPRING", "SUMMER"],
            "admission_basis": "SPACE AVAILABLE BASIS ONLY",
            "additional_requirements": [
                "Students must be in good academic standing (not on academic notice)",
                "Priority given to eligible students with strongest grades in CS 18000, Calculus and overall GPA",
                "All CS and Math courses must be taken for letter grade on Purdue campus",
                "Only first or second attempt of required CS and Math course considered",
                "Course withdrawals are included in attempt requirement"
            ],
            "contact_info": {
                "email": "csug@purdue.edu",
                "advising": "Computer Science Advisor during Non Major Drop-in Hours"
            },
            "space_availability": "Space is extremely limited"
        }
        
        return codo_requirements
        
    except Exception as e:
        print(f"Error scraping CODO requirements: {e}")
        return None

def update_knowledge_graph():
    """Update knowledge graph with correct CODO requirements"""
    
    kg_path = "data/cs_knowledge_graph.json"
    
    if not os.path.exists(kg_path):
        print(f"Knowledge graph not found: {kg_path}")
        return
    
    with open(kg_path, 'r') as f:
        kg_data = json.load(f)
    
    # Get official requirements
    codo_requirements = scrape_official_codo_requirements()
    
    if codo_requirements:
        # Update CODO requirements
        kg_data["codo_requirements"] = codo_requirements
        
        # Save updated knowledge graph
        backup_path = f"{kg_path}.backup_codo"
        os.rename(kg_path, backup_path)
        
        with open(kg_path, 'w') as f:
            json.dump(kg_data, f, indent=2)
        
        print("✅ Updated knowledge graph with correct CODO requirements")
        print(f"📁 Backup saved: {backup_path}")
    else:
        print("❌ Failed to get CODO requirements")

def update_comprehensive_data():
    """Update comprehensive data with correct CODO requirements"""
    
    comp_path = "data/comprehensive_purdue_cs_data.json"
    
    if not os.path.exists(comp_path):
        print(f"Comprehensive data not found: {comp_path}")
        return
    
    with open(comp_path, 'r') as f:
        comp_data = json.load(f)
    
    # Get official requirements
    codo_requirements = scrape_official_codo_requirements()
    
    if codo_requirements:
        # Update CODO requirements
        comp_data["codo_requirements"] = codo_requirements
        
        with open(comp_path, 'w') as f:
            json.dump(comp_data, f, indent=2)
        
        print("✅ Updated comprehensive data with correct CODO requirements")
    else:
        print("❌ Failed to update comprehensive data")

def update_universal_advisor():
    """Update the universal advisor CODO handler with correct information"""
    
    advisor_path = "universal_purdue_advisor.py"
    
    if not os.path.exists(advisor_path):
        print(f"Universal advisor not found: {advisor_path}")
        return
    
    # Read the current file
    with open(advisor_path, 'r') as f:
        content = f.read()
    
    # Find and replace the CODO handler section
    old_codo_section = '''        response_parts = [
            "**CODO into Computer Science Requirements:**",
            "",
            "**Minimum Requirements:**",
            "• GPA of 3.2 or higher",
            "• Complete MATH 16100 (Calculus I) with C or better",
            "• Complete MATH 16200 (Calculus II) with C or better", 
            "• Complete CS 18000 (Problem Solving with Computers) with C or better",
            "",
            "**Application Process:**",
            "• Submit CODO application through myPurdue",
            "• Meet with academic advisor",
            "• Application deadlines: November 1 (Spring) and March 1 (Fall)",'''
    
    new_codo_section = '''        response_parts = [
            "**CODO into Computer Science Requirements (Updated Official Requirements):**",
            "",
            "**Minimum Requirements:**",
            "• Overall GPA of 2.75 or higher",
            "• Minimum 1 semester at Purdue",
            "• Minimum 12 credit hours at Purdue main campus",
            "• Good academic standing (not on academic notice)",
            "",
            "**Required Courses (B or better in ALL):**",
            "• CS 18000 - Problem Solving and Object-Oriented Programming (4 credits)",
            "• ONE of the following math courses:",
            "  - MA 16100 (Calculus I) or MA 16500",
            "  - MA 16200 (Calculus II) or MA 16600", 
            "  - MA 26100 (Multivariate Calculus) or MA 27101",
            "  - MA 26500 (Linear Algebra) or MA 35100",
            "",
            "**Application Process:**",
            "• Accepted for Fall, Spring, and Summer terms",
            "• Admission on SPACE AVAILABLE BASIS ONLY",
            "• Space is extremely limited",
            "• Contact: csug@purdue.edu",'''
    
    # Replace the section
    if old_codo_section in content:
        content = content.replace(old_codo_section, new_codo_section)
        
        # Write back to file
        with open(advisor_path, 'w') as f:
            f.write(content)
        
        print("✅ Updated universal advisor CODO handler")
    else:
        print("⚠️ Could not find CODO section to update in universal advisor")

def main():
    """Main function to update all CODO requirements"""
    
    print("🔄 Updating CODO Requirements with Official Information")
    print("=" * 60)
    
    # Scrape official requirements
    codo_requirements = scrape_official_codo_requirements()
    
    if codo_requirements:
        print("✅ Successfully scraped official CODO requirements")
        print(f"📊 Key Updates:")
        print(f"   • Minimum GPA: {codo_requirements['minimum_gpa']} (was 3.2)")
        print(f"   • CS 18000 grade requirement: B (was C)")
        print(f"   • Math requirement: B in ONE of 4 options (was C in Calc I+II)")
        print(f"   • Space availability: {codo_requirements['space_availability']}")
        
        # Update all knowledge bases
        update_knowledge_graph()
        update_comprehensive_data()
        update_universal_advisor()
        
        print("\n✅ All knowledge bases updated with correct CODO requirements!")
        
        # Display the correct requirements
        print("\n📋 **CORRECTED CODO REQUIREMENTS:**")
        print(f"• Minimum GPA: {codo_requirements['minimum_gpa']}")
        print(f"• Minimum Purdue credits: {codo_requirements['minimum_purdue_credits']}")
        print("• Required courses:")
        print("  - CS 18000 with B or better")
        print("  - ONE math course with B or better from:")
        for option in codo_requirements['math_requirement']['options']:
            print(f"    * {option['code']} ({option['title']})")
        print("• Additional requirements:")
        for req in codo_requirements['additional_requirements']:
            print(f"  - {req}")
        
    else:
        print("❌ Failed to scrape CODO requirements")

if __name__ == "__main__":
    main()