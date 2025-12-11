#!/usr/bin/env python3
"""
Simple test runner for Agent Logic Simulation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'test_agent_logic_fixed.py'))

from test_agent_logic_fixed import AgentLogicTestSuite

def main():
    """Run tests and display results"""
    print("=" * 80)
    print("    PHASE 3: AGENT LOGIC SIMULATION - ALPHAAXIOM SYSTEM")
    print("=" * 80)
    
    # Initialize and run test suite
    test_suite = AgentLogicTestSuite()
    report = test_suite.run_all_tests()
    
    # Display results
    print(f"\n📊 TEST SUMMARY")
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    print(f"Execution Time: {report['summary']['total_execution_time']:.2f}s")
    
    print(f"\n📋 CATEGORY BREAKDOWN")
    for category, results in report['category_breakdown'].items():
        print(f"{category}: {results['passed']}/{results['total']} ({results['pass_rate']:.1f}%)")
    
    # Save detailed report
    with open('agent_logic_test_report_final.json', 'w') as f:
        import json
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: agent_logic_test_report_final.json")
    print(f"📝 Test log saved to: agent_logic_test_fixed.log")
    
    print("\n" + "=" * 80)
    if report['summary']['pass_rate'] >= 90:
        print("    🎉 EXCELLENT: Agent Logic Simulation PASSED")
    elif report['summary']['pass_rate'] >= 75:
        print("    ✅ GOOD: Agent Logic Simulation MOSTLY PASSED")
    else:
        print("    ⚠️  NEEDS IMPROVEMENT: Agent Logic Simulation FAILED")
    print("=" * 80)

if __name__ == "__main__":
    main()