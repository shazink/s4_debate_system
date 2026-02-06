"""
Generate example debate log: Active debate scenario
Query: "Should I invest my life savings in Bitcoin?"
Expected: Agents disagree initially, debate, some change minds
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.coordinator import Coordinator
import json

def main():
    print("="*80)
    print(" GENERATING ACTIVE DEBATE EXAMPLE")
    print("="*80)
    
    coordinator = Coordinator(save_logs=False)
    
    # Controversial query - should trigger debate
    query = "Should I invest my life savings in Bitcoin?"
    
    print(f"\nQuery: {query}\n")
    print("Running debate (this will take ~10-15 seconds)...")
    
    result = coordinator.run_debate(query)
    
    print(f"\nFinal Decision: {result.final_decision}")
    print(f"Reasoning: {result.reasoning}\n")
    
    # Save to JSON
    output = {
        "scenario": "Active Debate - Disagreement & Revision",
        "query": query,
        "rounds": result.debate_summary.get("rounds", []),
        "final_decision": {
            "decision": result.final_decision,
            "reasoning": result.reasoning,
            "metadata": result.metadata
        }
    }
    
    with open("examples/debate_example.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("✅ Saved to examples/debate_example.json")
    print("\nKey Points:")
    print("- Check Round 1: Agents likely had different initial decisions")
    print("- Check Round 2: See actual challenges between agents")
    print("- Check Round 3: Look for position changes (ACT→WARN, etc.)")
    print("- Final: Agreement % may be <100% or agents converged after debate")

if __name__ == "__main__":
    main()
