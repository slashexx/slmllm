from orchestrator import HybridOrchestrator


def main():
    orchestrator = HybridOrchestrator()
    
    examples = [
        "What is the capital of France?",
        "Explain quantum computing and its applications in machine learning",
        "Hello, how are you?",
        "Design a distributed system architecture for handling 10 million concurrent users",
        "Compare and contrast REST APIs vs GraphQL, including performance implications"
    ]
    
    print("=" * 60)
    print("LLM-SLM Router Examples")
    print("=" * 60)
    
    for i, prompt in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(f"Prompt: {prompt}")
        print("-" * 60)
        
        try:
            result = orchestrator.process(prompt, priority="balanced")
            
            print(f"Model Used: {result['model_used'].upper()}")
            print(f"Decision Confidence: {result['decision'].confidence:.2f}")
            print(f"Reason: {result['decision'].reason}")
            print(f"Estimated Cost: ${result['decision'].estimated_cost:.6f}")
            print(f"Estimated Latency: {result['decision'].estimated_latency:.2f}s")
            if result['fallback_used']:
                print(f"Fallback Used: Yes - {result.get('fallback_reason', 'N/A')}")
            print(f"\nResponse Preview: {result['response'][:200]}...")
        
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("=" * 60)


if __name__ == "__main__":
    main()

