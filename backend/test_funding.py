import sys
import os
import json
sys.path.append(os.getcwd())

from app.agents.funding_agent import FundingAgent

def main():
    agent = FundingAgent()
    
    print("Running FundingAgent Negative Test (OpenAI)...")
    signals = agent.collect("OpenAI", "test-openai")
    print(f"OpenAI Signals Found: {len(signals)}")
    for s in signals:
        print(json.dumps(s, indent=2))
        
    print("\nRunning FundingAgent Positive Test (xAI)...")
    signals = agent.collect("xAI", "test-xai")
    print(f"xAI Signals Found: {len(signals)}")
    for s in signals:
        print(json.dumps(s, indent=2))

if __name__ == "__main__":
    main()
