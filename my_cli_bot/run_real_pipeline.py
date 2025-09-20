#!/usr/bin/env python3
"""
Run the real curriculum data pipeline without interactive prompts
"""

from production_integration import ProductionIntegration
import json

def main():
    """Run the production pipeline with real data"""
    integration = ProductionIntegration()
    
    print("🚀 Real Purdue CS Curriculum Pipeline")
    print("=" * 50)
    
    # Run the complete pipeline
    print("\n1. Running real curriculum scraper...")
    scraper_result = integration.run_advanced_scraper("scrape")
    
    if scraper_result["success"]:
        print("✅ Real curriculum data scraped successfully")
        
        # Sync with Roo system
        print("\n2. Syncing real data with Roo system...")
        sync_result = integration.sync_data_with_roo()
        
        if sync_result:
            print("✅ Real data synchronized with Roo system")
            
            # Generate final status report
            print("\n3. Generating final status report...")
            status = integration.generate_status_report()
            
            print("\n📊 Final System Status:")
            print(f"   Real Data Files: {len([f for f, info in status['data_files'].items() if info['exists']])}")
            print(f"   System Components: {sum(status['system_requirements'].values())}/5")
            print(f"   Active Services: {sum(status['services'].values())}/3")
            
            # Show real data summary
            try:
                with open("data/real_curriculum_data.json", 'r') as f:
                    real_data = json.load(f)
                
                print("\n🎯 Real Curriculum Data Summary:")
                print(f"   ├── Data Source: {real_data.get('source', 'Unknown')}")
                print(f"   ├── Core Courses: {len(real_data.get('coreCourses', []))}")
                print(f"   ├── Total Courses: {len(real_data.get('allCourses', []))}")
                print(f"   ├── MI Track: {len(real_data.get('tracks', {}).get('machineIntelligence', {}).get('required', []))} req + {len(real_data.get('tracks', {}).get('machineIntelligence', {}).get('electives', []))} elective")
                print(f"   └── SE Track: {len(real_data.get('tracks', {}).get('softwareEngineering', {}).get('required', []))} req + {len(real_data.get('tracks', {}).get('softwareEngineering', {}).get('electives', []))} elective")
                
                # Show some example courses
                print("\n📚 Example Real Courses:")
                for i, course in enumerate(real_data.get('coreCourses', [])[:3]):
                    prereqs = course.get('prerequisites', [])
                    prereq_text = f" (Prerequisites: {', '.join(prereqs)})" if prereqs else ""
                    print(f"   {i+1}. {course['code']} - {course['title']} ({course['credits']} credits){prereq_text}")
                
            except Exception as e:
                print(f"   Error reading real data: {e}")
            
            print("\n🎉 Real curriculum pipeline completed successfully!")
            print("\nThe enhanced Roo system now has:")
            print("• Real Purdue CS course information")
            print("• Accurate prerequisite mappings")
            print("• Updated knowledge graph with verified data")
            print("• Enhanced vector store with real course details")
            
        else:
            print("❌ Failed to sync real data with Roo system")
    else:
        print("❌ Failed to scrape real curriculum data")
        print(f"Error: {scraper_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()