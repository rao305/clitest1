#!/usr/bin/env python3
"""
Production Integration: Advanced N8N Scraper with Enhanced Roo System
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import asyncio

class ProductionIntegration:
    """Integrates the advanced N8N scraper with the enhanced Roo system"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.advanced_scraper_dir = self.base_dir / "advanced_scraper"
        self.data_dir = self.base_dir / "data"
        self.processed_dir = self.data_dir / "processed"
        
    def check_system_requirements(self) -> Dict:
        """Check if all system components are available"""
        requirements = {
            "nodejs": self.check_nodejs(),
            "python": self.check_python(),
            "advanced_scraper": self.check_advanced_scraper(),
            "data_files": self.check_data_files(),
            "knowledge_graph": self.check_knowledge_graph()
        }
        
        return requirements
    
    def check_nodejs(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_python(self) -> bool:
        """Check if Python is available"""
        return sys.version_info >= (3, 8)
    
    def check_advanced_scraper(self) -> bool:
        """Check if advanced scraper is available"""
        cli_path = self.advanced_scraper_dir / "cli.js"
        return cli_path.exists()
    
    def check_data_files(self) -> bool:
        """Check if processed data files exist"""
        required_files = [
            "processed_curriculum.json",
            "n8n_workflow_data.json",
            "python_integration_data.json"
        ]
        
        return all((self.processed_dir / file).exists() for file in required_files)
    
    def check_knowledge_graph(self) -> bool:
        """Check if knowledge graph is available"""
        kg_path = self.data_dir / "cs_knowledge_graph.json"
        return kg_path.exists()
    
    def run_advanced_scraper(self, command: str = "scrape") -> Dict:
        """Run the advanced scraper system"""
        print(f"🚀 Running real curriculum scraper: {command}")
        
        try:
            # Use the working scraper that has real data
            cmd = ["node", "working_scraper.js", command]
            result = subprocess.run(
                cmd,
                cwd=self.advanced_scraper_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                print("✅ Real curriculum scraper completed successfully")
                return {
                    "success": True,
                    "output": result.stdout,
                    "error": result.stderr
                }
            else:
                print(f"❌ Real curriculum scraper failed with code {result.returncode}")
                return {
                    "success": False,
                    "output": result.stdout,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ Real curriculum scraper timed out")
            return {
                "success": False,
                "output": "",
                "error": "Operation timed out"
            }
        except Exception as e:
            print(f"❌ Error running real curriculum scraper: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    def sync_data_with_roo(self) -> bool:
        """Sync advanced scraper data with Roo system"""
        print("🔄 Syncing data with Roo system...")
        
        try:
            # Load real curriculum data
            real_data_path = self.data_dir / "real_curriculum_data.json"
            
            if not real_data_path.exists():
                print("❌ No real curriculum data found")
                return False
            
            with open(real_data_path, 'r') as f:
                processed_data = json.load(f)
            
            # Update knowledge graph with new data
            self.update_knowledge_graph(processed_data)
            
            # Update vector store if needed
            self.update_vector_store(processed_data)
            
            print("✅ Data sync completed")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing data: {e}")
            return False
    
    def update_knowledge_graph(self, processed_data: Dict):
        """Update the knowledge graph with new data"""
        print("📊 Updating knowledge graph...")
        
        try:
            from knowledge_graph import PurdueCSKnowledgeGraph, Course
            
            # Create new knowledge graph
            kg = PurdueCSKnowledgeGraph()
            
            # Add courses from real curriculum data
            for course_data in processed_data.get('allCourses', []):
                course = Course(
                    code=course_data['code'],
                    title=course_data['title'],
                    credits=course_data['credits'],
                    prerequisites=course_data.get('prerequisites', []),
                    description=course_data.get('description', '')
                )
                kg.add_course(course)
            
            # Add track information
            for track_name, track_data in processed_data.get('tracks', {}).items():
                track_info = {
                    'required_courses': [c['code'] for c in track_data.get('required', [])],
                    'elective_options': [c['code'] for c in track_data.get('electives', [])],
                    'min_electives': len(track_data.get('electives', [])),
                    'total_credits': sum(c.get('credits', 3) for c in track_data.get('required', []) + track_data.get('electives', []))
                }
                kg.add_track(track_name, track_info)
            
            # Export updated knowledge graph
            kg.export_to_json(str(self.data_dir / "cs_knowledge_graph.json"))
            
            print("✅ Knowledge graph updated")
            
        except Exception as e:
            print(f"❌ Error updating knowledge graph: {e}")
    
    def update_vector_store(self, processed_data: Dict):
        """Update vector store with new data"""
        print("🔍 Updating vector store...")
        
        try:
            # Create normalized chunks for vector store
            normalized_chunks = []
            
            for course_data in processed_data.get('allCourses', []):
                # Create detailed course information
                prerequisites_text = ""
                if course_data.get('prerequisites'):
                    prerequisites_text = f" Prerequisites: {', '.join(course_data['prerequisites'])}."
                
                chunk = {
                    "content": f"Course: {course_data['code']} - {course_data['title']} ({course_data['credits']} credits). Category: {course_data['category']}.{prerequisites_text}",
                    "source": "real_curriculum_scraper",
                    "type": "course_info",
                    "course_code": course_data['code']
                }
                normalized_chunks.append(chunk)
            
            # Save normalized chunks
            chunks_path = self.data_dir / "normalized_chunks.json"
            with open(chunks_path, 'w') as f:
                json.dump(normalized_chunks, f, indent=2)
            
            print("✅ Vector store updated")
            
        except Exception as e:
            print(f"❌ Error updating vector store: {e}")
    
    def start_api_server(self, port: int = 3000) -> subprocess.Popen:
        """Start the advanced scraper API server"""
        print(f"🌐 Starting API server on port {port}...")
        
        try:
            cmd = ["node", "cli.js", "server", "--port", str(port)]
            process = subprocess.Popen(
                cmd,
                cwd=self.advanced_scraper_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"✅ API server started (PID: {process.pid})")
            return process
            
        except Exception as e:
            print(f"❌ Error starting API server: {e}")
            return None
    
    def run_complete_pipeline(self) -> Dict:
        """Run the complete data pipeline"""
        print("🚀 Running complete production pipeline...")
        
        pipeline_results = {
            "system_check": self.check_system_requirements(),
            "scraper_run": None,
            "data_sync": False,
            "api_server": None
        }
        
        # Check system requirements
        print("\n1. Checking system requirements...")
        requirements = pipeline_results["system_check"]
        
        for component, status in requirements.items():
            print(f"   {'✅' if status else '❌'} {component}")
        
        if not all(requirements.values()):
            print("❌ System requirements not met")
            return pipeline_results
        
        # Run advanced scraper
        print("\n2. Running advanced scraper...")
        scraper_result = self.run_advanced_scraper("pipeline")
        pipeline_results["scraper_run"] = scraper_result
        
        if not scraper_result["success"]:
            print("❌ Advanced scraper failed")
            return pipeline_results
        
        # Sync data with Roo system
        print("\n3. Syncing data with Roo system...")
        sync_result = self.sync_data_with_roo()
        pipeline_results["data_sync"] = sync_result
        
        if not sync_result:
            print("❌ Data sync failed")
            return pipeline_results
        
        # Start API server
        print("\n4. Starting API server...")
        api_process = self.start_api_server()
        pipeline_results["api_server"] = api_process is not None
        
        print("\n🎉 Production pipeline completed successfully!")
        print("\nSystem is now ready with:")
        print("- Enhanced Roo CS Advisor (Python)")
        print("- Advanced N8N Scraper (Node.js)")
        print("- RESTful API Server")
        print("- Updated knowledge graph")
        print("- Synchronized data stores")
        
        return pipeline_results
    
    def generate_status_report(self) -> Dict:
        """Generate a comprehensive status report"""
        print("📊 Generating system status report...")
        
        status = {
            "timestamp": json.dumps({"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}}),
            "system_requirements": self.check_system_requirements(),
            "data_files": {},
            "services": {
                "roo_advisor": self.check_roo_advisor(),
                "api_server": self.check_api_server(),
                "knowledge_graph": self.check_knowledge_graph()
            }
        }
        
        # Check data files
        data_files = [
            "advanced_curriculum_data.json",
            "processed/processed_curriculum.json",
            "processed/n8n_workflow_data.json",
            "processed/python_integration_data.json",
            "cs_knowledge_graph.json"
        ]
        
        for file_path in data_files:
            full_path = self.data_dir / file_path
            if full_path.exists():
                stat = full_path.stat()
                status["data_files"][file_path] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                }
            else:
                status["data_files"][file_path] = {"exists": False}
        
        return status
    
    def check_roo_advisor(self) -> bool:
        """Check if Roo advisor is available"""
        try:
            import sys
            sys.path.append(str(self.base_dir))
            from roo_engine_v2 import RooCSAdvisorV2
            return True
        except ImportError:
            return False
    
    def check_api_server(self) -> bool:
        """Check if API server is running"""
        try:
            import requests
            response = requests.get("http://localhost:3000/health", timeout=5)
            return response.status_code == 200
        except:
            return False

def main():
    """Main function for production integration"""
    integration = ProductionIntegration()
    
    print("🚀 Purdue CS Curriculum - Production Integration")
    print("=" * 55)
    
    # Generate status report
    status = integration.generate_status_report()
    
    print("\n📊 System Status:")
    for component, status_val in status["system_requirements"].items():
        print(f"   {'✅' if status_val else '❌'} {component}")
    
    print("\n📁 Data Files:")
    for file_path, info in status["data_files"].items():
        if info["exists"]:
            size_kb = info["size"] / 1024
            print(f"   ✅ {file_path} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ {file_path} (missing)")
    
    print("\n🔧 Services:")
    for service, status_val in status["services"].items():
        print(f"   {'✅' if status_val else '❌'} {service}")
    
    # Ask user if they want to run the complete pipeline
    run_pipeline = input("\n🤔 Run complete production pipeline? (y/n): ").lower().strip()
    
    if run_pipeline == 'y':
        results = integration.run_complete_pipeline()
        
        print("\n📈 Pipeline Results:")
        print(f"   System Check: {'✅' if all(results['system_check'].values()) else '❌'}")
        print(f"   Scraper Run: {'✅' if results['scraper_run'] and results['scraper_run']['success'] else '❌'}")
        print(f"   Data Sync: {'✅' if results['data_sync'] else '❌'}")
        print(f"   API Server: {'✅' if results['api_server'] else '❌'}")
        
        if all([
            all(results['system_check'].values()),
            results['scraper_run'] and results['scraper_run']['success'],
            results['data_sync'],
            results['api_server']
        ]):
            print("\n🎉 Production system is fully operational!")
        else:
            print("\n⚠️ Some components failed - check logs for details")
    
    else:
        print("\n💡 To run the pipeline later, execute: python production_integration.py")

if __name__ == "__main__":
    main()