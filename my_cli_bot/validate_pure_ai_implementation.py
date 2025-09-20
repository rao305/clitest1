#!/usr/bin/env python3
"""
Pure AI Implementation Validation Script
Validates that the Boiler AI system is 100% AI-powered with no hardcoded responses
"""

import os
import re
import ast
import json
import subprocess
from typing import List, Dict, Any, Tuple
from pathlib import Path

class PureAIValidator:
    """Validates the pure AI implementation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.violations = []
        self.passed_checks = []
        self.warnings = []
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("🔍 Starting Pure AI Implementation Validation...")
        print("=" * 60)
        
        # Core validation checks
        self.check_hardcoded_responses()
        self.check_environment_configuration()
        self.check_error_handling()
        self.check_monitoring_integration()
        self.check_api_dependencies()
        self.check_fallback_mechanisms()
        
        # Generate report
        return self.generate_report()
    
    def check_hardcoded_responses(self):
        """Check for hardcoded response patterns in critical files only"""
        print("\n📝 Checking for hardcoded responses...")
        
        # Focus on critical files that should be 100% AI-powered
        critical_files = [
            'universal_purdue_advisor.py',
            'simple_boiler_ai.py', 
            'friendly_response_generator.py',
            'intelligent_conversation_manager.py'
        ]
        
        # More precise patterns for actual hardcoded responses
        hardcoded_patterns = [
            r'return\s*["\'][A-Z][^"\']{50,}["\']',  # Direct return of long response strings
            r'response\s*=\s*["\'][A-Z][^"\']{50,}["\']',  # Direct assignment of response strings
            r'fallback.*=.*\[.*["\'][A-Z][^"\']{20,}["\']',  # Fallback arrays with responses
            r'print\(["\'][A-Z][^"\']{30,}["\']',  # Direct print of long user-facing messages
        ]
        
        found_violations = False
        
        for filename in critical_files:
            file_path = self.project_root / filename
            if not file_path.exists():
                self.warnings.append(f"Critical file {filename} not found")
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for i, line in enumerate(content.split('\n'), 1):
                    # Skip comments and docstrings
                    if line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''"):
                        continue
                    
                    for pattern in hardcoded_patterns:
                        if re.search(pattern, line):
                            # Additional filters to avoid false positives
                            if ('prompt' not in line.lower() and 
                                'ai_engine' not in line.lower() and 
                                'Gemini' not in line.lower() and
                                'generate' not in line.lower() and
                                'logger' not in line.lower()):
                                
                                self.violations.append({
                                    'type': 'hardcoded_response',
                                    'file': str(file_path.name),
                                    'line': i,
                                    'content': line.strip()[:100] + "..." if len(line.strip()) > 100 else line.strip(),
                                    'severity': 'high'
                                })
                                found_violations = True
                            
            except Exception as e:
                self.warnings.append(f"Could not read {filename}: {str(e)}")
        
        if not found_violations:
            self.passed_checks.append("✅ No hardcoded responses found in critical AI files")
        else:
            violation_count = len([v for v in self.violations if v['type'] == 'hardcoded_response'])
            print(f"❌ Found {violation_count} hardcoded response violations in critical files")
    
    def check_environment_configuration(self):
        """Check environment configuration completeness"""
        print("\n🔧 Checking environment configuration...")
        
        env_template_path = self.project_root / '.env.template'
        required_keys = [
            'GEMINI_API_KEY',
            'ANTHROPIC_API_KEY', 
            'GEMINI_API_KEY',
            'CLADO_API_KEY',
            'ENABLE_TOKEN_MONITORING',
            'MAX_TOKENS_PER_HOUR',
            'ENABLE_ERROR_LOGGING',
            'ENABLE_PERFORMANCE_LOGGING'
        ]
        
        if not env_template_path.exists():
            self.violations.append({
                'type': 'missing_env_template',
                'file': '.env.template',
                'severity': 'high',
                'message': 'Environment template file missing'
            })
        else:
            try:
                with open(env_template_path, 'r') as f:
                    env_content = f.read()
                
                missing_keys = []
                for key in required_keys:
                    if key not in env_content:
                        missing_keys.append(key)
                
                if missing_keys:
                    self.violations.append({
                        'type': 'incomplete_env_config',
                        'file': '.env.template',
                        'severity': 'medium',
                        'message': f'Missing environment keys: {", ".join(missing_keys)}'
                    })
                else:
                    self.passed_checks.append("✅ Environment configuration is complete")
                    
            except Exception as e:
                self.warnings.append(f"Could not read .env.template: {str(e)}")
    
    def check_error_handling(self):
        """Check error handling robustness"""
        print("\n🛡️ Checking error handling...")
        
        # Look for proper error handling in key files
        key_files = ['simple_boiler_ai.py', 'universal_purdue_advisor.py', 'friendly_response_generator.py']
        
        for filename in key_files:
            file_path = self.project_root / filename
            if not file_path.exists():
                self.warnings.append(f"Key file {filename} not found")
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for try-except blocks
                try_except_count = len(re.findall(r'try:', content))
                except_count = len(re.findall(r'except.*:', content))
                
                if try_except_count < 2 or except_count < 2:
                    self.violations.append({
                        'type': 'insufficient_error_handling',
                        'file': filename,
                        'severity': 'medium',
                        'message': f'Only {try_except_count} try blocks and {except_count} except blocks found'
                    })
                else:
                    self.passed_checks.append(f"✅ {filename} has adequate error handling")
                    
            except Exception as e:
                self.warnings.append(f"Could not analyze error handling in {filename}: {str(e)}")
    
    def check_monitoring_integration(self):
        """Check monitoring system integration"""
        print("\n📊 Checking monitoring integration...")
        
        monitoring_file = self.project_root / 'ai_monitoring_system.py'
        if not monitoring_file.exists():
            self.violations.append({
                'type': 'missing_monitoring',
                'file': 'ai_monitoring_system.py',
                'severity': 'medium',
                'message': 'Monitoring system file not found'
            })
            return
        
        # Check for monitoring integration in main AI file
        main_ai_file = self.project_root / 'simple_boiler_ai.py'
        if main_ai_file.exists():
            try:
                with open(main_ai_file, 'r') as f:
                    content = f.read()
                
                if 'from ai_monitoring_system import' in content and 'record_api_call' in content:
                    self.passed_checks.append("✅ Monitoring system is integrated")
                else:
                    self.violations.append({
                        'type': 'monitoring_not_integrated',
                        'file': 'simple_boiler_ai.py',
                        'severity': 'medium',
                        'message': 'Monitoring system not properly integrated'
                    })
            except Exception as e:
                self.warnings.append(f"Could not check monitoring integration: {str(e)}")
    
    def check_api_dependencies(self):
        """Check API dependency management"""
        print("\n🔌 Checking API dependencies...")
        
        # Check for proper API key validation
        key_files = ['simple_boiler_ai.py', 'llm_providers.py']
        
        for filename in key_files:
            file_path = self.project_root / filename
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for API key validation
                if 'GEMINI_API_KEY' in content and 'os.environ.get' in content:
                    self.passed_checks.append(f"✅ {filename} has proper API key handling")
                else:
                    self.warnings.append(f"{filename} may not have proper API key validation")
                    
            except Exception as e:
                self.warnings.append(f"Could not check API dependencies in {filename}: {str(e)}")
    
    def check_fallback_mechanisms(self):
        """Check for proper fallback mechanisms"""
        print("\n🔄 Checking fallback mechanisms...")
        
        # Check for multi-provider support
        llm_providers_file = self.project_root / 'llm_providers.py'
        if llm_providers_file.exists():
            try:
                with open(llm_providers_file, 'r') as f:
                    content = f.read()
                
                providers = ['Gemini', 'Anthropic', 'Gemini']
                found_providers = [p for p in providers if f'{p}Provider' in content]
                
                if len(found_providers) >= 2:
                    self.passed_checks.append(f"✅ Multi-provider fallback support found: {', '.join(found_providers)}")
                else:
                    self.violations.append({
                        'type': 'insufficient_fallback',
                        'file': 'llm_providers.py',
                        'severity': 'medium',
                        'message': f'Only {len(found_providers)} provider(s) found: {found_providers}'
                    })
                    
            except Exception as e:
                self.warnings.append(f"Could not check fallback mechanisms: {str(e)}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        # Calculate scores
        total_checks = len(self.passed_checks) + len(self.violations)
        success_rate = (len(self.passed_checks) / total_checks * 100) if total_checks > 0 else 0
        
        # Categorize violations by severity
        high_severity = [v for v in self.violations if v.get('severity') == 'high']
        medium_severity = [v for v in self.violations if v.get('severity') == 'medium']
        
        # Generate recommendations
        recommendations = []
        if high_severity:
            recommendations.append("🚨 CRITICAL: Fix high-severity violations immediately")
        if medium_severity:
            recommendations.append("⚠️ IMPORTANT: Address medium-severity issues for production readiness")
        if success_rate < 80:
            recommendations.append("📈 IMPROVEMENT: System needs significant improvements for pure AI compliance")
        elif success_rate < 95:
            recommendations.append("🔧 REFINEMENT: Minor improvements needed for optimal pure AI operation")
        else:
            recommendations.append("✅ EXCELLENT: System meets pure AI implementation standards")
        
        report = {
            'validation_timestamp': os.path.basename(__file__),
            'overall_score': success_rate,
            'status': 'PASS' if success_rate >= 90 and not high_severity else 'FAIL',
            'summary': {
                'total_checks': total_checks,
                'passed_checks': len(self.passed_checks),
                'violations': len(self.violations),
                'warnings': len(self.warnings),
                'high_severity_violations': len(high_severity),
                'medium_severity_violations': len(medium_severity)
            },
            'passed_checks': self.passed_checks,
            'violations': self.violations,
            'warnings': self.warnings,
            'recommendations': recommendations
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted validation report"""
        print("\n" + "=" * 60)
        print("🎯 PURE AI IMPLEMENTATION VALIDATION REPORT")
        print("=" * 60)
        
        # Overall status
        status_emoji = "✅" if report['status'] == 'PASS' else "❌"
        print(f"\n{status_emoji} Overall Status: {report['status']}")
        print(f"📊 Success Rate: {report['overall_score']:.1f}%")
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"   Total Checks: {report['summary']['total_checks']}")
        print(f"   Passed: {report['summary']['passed_checks']}")
        print(f"   Violations: {report['summary']['violations']}")
        print(f"   Warnings: {report['summary']['warnings']}")
        
        # Violations by severity
        if report['summary']['high_severity_violations'] > 0:
            print(f"   🚨 High Severity: {report['summary']['high_severity_violations']}")
        if report['summary']['medium_severity_violations'] > 0:
            print(f"   ⚠️ Medium Severity: {report['summary']['medium_severity_violations']}")
        
        # Passed checks
        if report['passed_checks']:
            print(f"\n✅ Passed Checks ({len(report['passed_checks'])}):")
            for check in report['passed_checks']:
                print(f"   {check}")
        
        # Violations
        if report['violations']:
            print(f"\n❌ Violations ({len(report['violations'])}):")
            for violation in report['violations']:
                severity_emoji = "🚨" if violation.get('severity') == 'high' else "⚠️"
                print(f"   {severity_emoji} {violation['type']} in {violation['file']}")
                if 'line' in violation:
                    print(f"      Line {violation['line']}: {violation.get('content', violation.get('message', ''))}")
                else:
                    print(f"      {violation.get('message', '')}")
        
        # Warnings
        if report['warnings']:
            print(f"\n⚠️ Warnings ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"   {warning}")
        
        # Recommendations
        print(f"\n🎯 Recommendations:")
        for rec in report['recommendations']:
            print(f"   {rec}")
        
        print("\n" + "=" * 60)

def main():
    """Main validation execution"""
    validator = PureAIValidator()
    report = validator.validate_all()
    validator.print_report(report)
    
    # Save report to file
    report_file = Path(__file__).parent / 'pure_ai_validation_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    exit_code = 0 if report['status'] == 'PASS' else 1
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)