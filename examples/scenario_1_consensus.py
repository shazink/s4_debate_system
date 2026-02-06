"""
Generate example debate log: Consensus scenario
Query: "What is the capital of France?"
Expected: All agents agree → ACT
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.coordinator import Coordinator
import json

def main():
    print("="*80)
    print(" GENERATING CONSENSUS EXAMPLE")
    print("="*80)
    
    coordinator = Coordinator(save_logs=False)
    
    # Simple factual query - should get unanimous ACT
    query = "What is the capital of France?"
    
    print(f"\nQuery: {query}\n")
    print("Running debate...")
    
    result = coordinator.run_debate(query)
    
    print(f"\nFinal Decision: {result.final_decision}")
    print(f"Reasoning: {result.reasoning}\n")
    
    # Save to JSON
    output = {
        "scenario": "Consensus - Unanimous Agreement",
        "query": query,
        "rounds": result.debate_summary.get("rounds", []),
        "final_decision": {
            "decision": result.final_decision,
            "reasoning": result.reasoning,
            "metadata": result.metadata
        }
    }
    
    with open("examples/consensus_example.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("✅ Saved to examples/consensus_example.json")
    print("\nKey Points:")
    print("- All 3 agents voted the same way")
    print("- 100% agreement")
    print("- Minimal debate (all agree from start)")
    print("- Fast, confident ACT decision")

if __name__ == "__main__":
    main()
