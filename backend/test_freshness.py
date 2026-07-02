import asyncio
from app.analysis.hypothesis_engine import HypothesisQualityValidator

def main():
    validator = HypothesisQualityValidator()
    
    # Test 1: O3 (Should Fail)
    # Evidence: "OpenAI and Broadcom unveil custom AI inference chip"
    # Prediction: "OpenAI will announce a custom AI chip"
    print("Testing O3 (Should Fail)")
    res_o3 = validator.run_create_deterministic_gate(
        belief="OpenAI is prioritizing hardware infrastructure over software partnerships as a strategic bet.",
        prediction="OpenAI will announce a custom AI chip",
        company_name="OpenAI",
        evidence_titles=["OpenAI and Broadcom unveil custom AI inference chip"]
    )
    print("O3 Result:", res_o3)
    
    # Test 2: O1 (Should Pass)
    # Evidence: "OpenAI signed LiveRamp and Getty agreements"
    # Prediction: "OpenAI will launch an enterprise data platform within 12 months"
    print("\nTesting O1 (Should Pass)")
    res_o1 = validator.run_create_deterministic_gate(
        belief="OpenAI is prioritizing data partnerships over proprietary data collection to build their enterprise moat.",
        prediction="OpenAI will launch an enterprise data platform within 12 months",
        company_name="OpenAI",
        evidence_titles=["OpenAI signed LiveRamp and Getty agreements"]
    )
    print("O1 Result:", res_o1)
    
if __name__ == "__main__":
    main()
