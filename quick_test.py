#!/usr/bin/env python3
"""
Quick test script for quantum computations
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

async def test_simple_computation():
    """Test a simple quantum computation"""
    print("🧪 Quick Quantum Test")
    print("=" * 50)
    
    try:
        # Import the client
        from client import SimpleQuantumClient
        
        # Create client
        client = SimpleQuantumClient()
        
        # Check API keys
        if not client.openai_key:
            print("❌ OPENAI_API_KEY not found")
            return False
        
        if not client.ibm_token:
            print("❌ IBM_QUANTUM_TOKEN not found")
            return False
        
        print(f"✅ API keys found")
        print(f"   OpenAI: {client.openai_key[:8]}...")
        print(f"   IBM: {client.ibm_token[:8]}...")
        
        # Run a simple quantum computation
        print("\n🚀 Testing Bell state creation...")
        result = await client.run_computation(
            "Create a simple Bell state with 2 qubits",
            shots=1024
        )
        
        if result:
            print("✅ Quantum computation completed!")
            return True
        else:
            print("❌ Quantum computation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_multiple_computations():
    """Test multiple quantum computations"""
    print("\n🧪 Multiple Quantum Tests")
    print("=" * 50)
    
    try:
        from client import SimpleQuantumClient
        client = SimpleQuantumClient()
        
        if not client.openai_key or not client.ibm_token:
            print("❌ API keys not found")
            return False
        
        tests = [
            "Create a Bell state",
            "Generate random numbers with 3 qubits", 
            "Apply Hadamard gates to 2 qubits"
        ]
        
        success_count = 0
        
        for i, test in enumerate(tests, 1):
            print(f"\n🔬 Test {i}/{len(tests)}: {test}")
            try:
                result = await client.run_computation(test, shots=512)
                if result:
                    success_count += 1
                    print(f"✅ Test {i} passed")
                else:
                    print(f"❌ Test {i} failed")
            except Exception as e:
                print(f"❌ Test {i} error: {e}")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        print(f"\n📊 Results: {success_count}/{len(tests)} tests passed")
        return success_count == len(tests)
        
    except Exception as e:
        print(f"❌ Multiple tests failed: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'simple':
            success = asyncio.run(test_simple_computation())
            sys.exit(0 if success else 1)
        elif command == 'multiple':
            success = asyncio.run(test_multiple_computations())
            sys.exit(0 if success else 1)
        elif command == 'all':
            print("🚀 Running All Tests")
            print("=" * 60)
            
            simple_success = asyncio.run(test_simple_computation())
            if simple_success:
                multiple_success = asyncio.run(test_multiple_computations())
                success = simple_success and multiple_success
            else:
                success = False
            
            print(f"\n🎯 Final Result: {'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: simple, multiple, all")
    else:
        print("""
🧪 Quick Quantum Test Suite

Usage:
  python quick_test.py simple    # Single test
  python quick_test.py multiple  # Multiple tests  
  python quick_test.py all       # All tests

This will test your quantum computation setup quickly.
        """)

if __name__ == "__main__":
    main()