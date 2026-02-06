#!/usr/bin/env python3
"""
Main entry point for S4 Multi-Agent Debate System.
Run custom queries through the debate process.
"""

import sys
from agents.coordinator import Coordinator


def main():
    """Run a custom query through the debate system."""
    
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("Usage: python main.py \"Your query here\"")
        print("\nRunning with example query...")
        query = "Should we implement a new feature that tracks user behavior without consent?"
    
    # Create coordinator
    print("\n🚀 Initializing S4 Multi-Agent Debate System...")
    coordinator = Coordinator(save_logs=True)
    
    # Run debate
    result = coordinator.run_debate(query)
    
    # Print summary
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    print(f"Query: {query}")
    print(f"\nDecision: {result.final_decision}")
    print(f"\nReasoning:\n{result.reasoning}")
    print(f"\nMetadata:\n{result.metadata}")
    print("="*80 + "\n")
    
    return result


if __name__ == "__main__":
    main()
