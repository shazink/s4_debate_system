#!/usr/bin/env python3
"""
Scenario 1: High Confidence, Low Risk
Expected: All agents agree → ACT
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.coordinator import Coordinator


def main():
    print("\n" + "🧪"*40)
    print("TEST SCENARIO 1: HIGH CONFIDENCE, LOW RISK")
    print("Expected: All agents agree → Final Decision: ACT")
    print("🧪"*40 + "\n")
    
    # Create coordinator
    coordinator = Coordinator(save_logs=True)
    
    # Simple, clear query
    query = "What is 2 + 2?"
    
    # Run debate
    result = coordinator.run_debate(query)
    
    # Print result
    print("\n" + "="*80)
    print("TEST RESULT SUMMARY")
    print("="*80)
    print(f"Query: {query}")
    print(f"Final Decision: {result.final_decision}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Metadata: {result.metadata}")
    print("="*80 + "\n")
    
    # Validation
    expected = "ACT"
    if result.final_decision == expected:
        print(f"✅ TEST PASSED: Decision is '{expected}' as expected")
    else:
        print(f"❌ TEST FAILED: Expected '{expected}', got '{result.final_decision}'")
    
    return result


if __name__ == "__main__":
    main()
