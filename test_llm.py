"""Simple test script for LLM utilities."""
from utils.llm import call_llm
from pathlib import Path

print("Testing LLM utilities...")
print("-" * 50)

# Test call_llm
print("\n1. Testing call_llm('Say hello'):")
try:
    response = call_llm("Say hello", agent_name="test_agent")
    print(f"✓ Response: {response}")
except ValueError as e:
    print(f"✗ Error: {e}")
    print("  Make sure OPENAI_API_KEY is set in .env file")
except Exception as e:
    print(f"✗ Error: {e}")

# Check log file
print("\n2. Checking log file:")
log_file = Path("logs/llm_calls.log")
if log_file.exists():
    print(f"✓ Log file exists: {log_file}")
    print("\nLast log entry:")
    with open(log_file, "r") as f:
        lines = f.readlines()
        if lines:
            print(f"  {lines[-1].strip()}")
        else:
            print("  (log file is empty)")
else:
    print("✗ Log file not found")

print("\n" + "-" * 50)
print("Test complete!")

