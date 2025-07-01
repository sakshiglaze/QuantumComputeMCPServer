#!/usr/bin/env python3
"""
Fix Both APIs - Test Script
Tests and helps fix both OpenAI and IBM Quantum API issues
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_openai():
    """Test OpenAI API key"""
    print("🤖 Testing OpenAI API...")
    print("-" * 30)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return False
    
    print(f"Key format: {api_key[:8]}...")
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test with minimal request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=1
        )
        
        print("✅ OpenAI API key is VALID!")
        print(f"   Model: {response.model}")
        print(f"   Usage: {response.usage.total_tokens} tokens")
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ OpenAI API key is INVALID: {error_str[:100]}...")
        
        if "401" in error_str or "Unauthorized" in error_str:
            print("\n🔧 How to fix:")
            print("1. Go to: https://platform.openai.com/api-keys")
            print("2. Create a NEW API key (delete the old one)")
            print("3. Make sure it's a STANDARD key, not project-scoped")
            print("4. Update your .env file with the new key")
            print("5. Check your OpenAI account has billing/credits")
        
        return False

def test_ibm_quantum():
    """Test IBM Quantum token with different methods"""
    print("\n⚛️  Testing IBM Quantum...")
    print("-" * 30)
    
    token = os.getenv('IBM_QUANTUM_TOKEN')
    if not token:
        print("❌ IBM_QUANTUM_TOKEN not found in .env file")
        return False
    
    print(f"Token format: {token[:8]}...")
    
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        
        # Method 1: Try new IBM Quantum Platform
        print("\n🧪 Method 1: IBM Quantum Platform")
        try:
            QiskitRuntimeService.save_account(
                channel="ibm_quantum_platform",
                token=token,
                overwrite=True
            )
            service = QiskitRuntimeService(channel="ibm_quantum_platform")
            backends = list(service.backends())
            
            print(f"✅ IBM Quantum Platform WORKS! Found {len(backends)} backends")
            
            # Show some backends
            for backend in backends[:3]:
                status = "🟢 Up" if backend.status().operational else "🔴 Down"
                print(f"   • {backend.name}: {backend.num_qubits} qubits - {status}")
            
            return True, "ibm_quantum_platform"
            
        except Exception as e1:
            print(f"❌ Platform failed: {e1}")
            
            # Method 2: Try IBM Cloud
            print("\n🧪 Method 2: IBM Cloud")
            try:
                QiskitRuntimeService.save_account(
                    channel="ibm_cloud",
                    token=token,
                    overwrite=True
                )
                service = QiskitRuntimeService(channel="ibm_cloud")
                backends = list(service.backends())
                
                print(f"✅ IBM Cloud WORKS! Found {len(backends)} backends")
                return True, "ibm_cloud"
                
            except Exception as e2:
                print(f"❌ Cloud failed: {e2}")
                
                # Method 3: Try legacy (deprecated but might work)
                print("\n🧪 Method 3: Legacy IBM Quantum (deprecated)")
                try:
                    QiskitRuntimeService.save_account(
                        channel="ibm_quantum",
                        token=token,
                        overwrite=True
                    )
                    service = QiskitRuntimeService(channel="ibm_quantum")
                    backends = list(service.backends())
                    
                    print(f"⚠️  Legacy channel works but is deprecated!")
                    print(f"   Found {len(backends)} backends")
                    print("   ⚠️  This will stop working July 1st, 2025")
                    return True, "ibm_quantum"
                    
                except Exception as e3:
                    print(f"❌ Legacy failed: {e3}")
                    
                    print("\n🔧 All IBM methods failed! Here's how to fix:")
                    print("\n🚨 ACCOUNT MIGRATION REQUIRED")
                    print("Your IBM account needs to be migrated to the new platform.")
                    print("\nSteps:")
                    print("1. Go to: https://quantum.ibm.com/")
                    print("2. Sign in with your IBM ID")
                    print("3. Complete any migration steps shown")
                    print("4. Get a NEW API token from Account Settings")
                    print("5. If that doesn't work, try IBM Cloud:")
                    print("   → https://cloud.ibm.com/")
                    print("   → Sign up for IBM Cloud account")
                    print("   → Find Quantum services")
                    print("   → Get IBM Cloud API token")
                    
                    return False, None
    
    except ImportError:
        print("❌ qiskit-ibm-runtime not installed")
        print("Install with: pip install qiskit-ibm-runtime")
        return False, None

def create_working_env_template(openai_works, ibm_works, ibm_channel):
    """Create a template .env file with working configuration"""
    
    print("\n📝 Creating .env template...")
    
    template = """# Quantum MCP Server - Working Configuration
# Replace with your actual API keys

"""
    
    if openai_works:
        template += "# ✅ OpenAI key format is correct\n"
        template += f"OPENAI_API_KEY={os.getenv('OPENAI_API_KEY')}\n\n"
    else:
        template += "# ❌ OpenAI key needs to be updated\n"
        template += "# Get new key from: https://platform.openai.com/api-keys\n"
        template += "OPENAI_API_KEY=sk-your-new-openai-key-here\n\n"
    
    if ibm_works:
        template += f"# ✅ IBM Quantum working with channel: {ibm_channel}\n"
        template += f"IBM_QUANTUM_TOKEN={os.getenv('IBM_QUANTUM_TOKEN')}\n"
        template += f"IBM_QUANTUM_CHANNEL={ibm_channel}\n\n"
    else:
        template += "# ❌ IBM Quantum token needs to be updated\n"
        template += "# Get new token from: https://quantum.ibm.com/account\n"
        template += "IBM_QUANTUM_TOKEN=your-new-ibm-token-here\n"
        template += "IBM_QUANTUM_CHANNEL=ibm_quantum_platform\n\n"
    
    template += """# Optional settings
LOG_LEVEL=INFO
DEFAULT_SHOTS=1024
"""
    
    try:
        with open('.env.new', 'w') as f:
            f.write(template)
        print("✅ Created .env.new template file")
        print("   Review it and rename to .env when ready")
    except:
        print("⚠️  Could not create .env.new file")
        print("Here's the template:")
        print(template)

def main():
    """Run all tests and provide fix guidance"""
    
    print("🔧 API Key Diagnostic Tool")
    print("=" * 40)
    
    # Test OpenAI
    openai_works = test_openai()
    
    # Test IBM Quantum  
    ibm_result = test_ibm_quantum()
    if isinstance(ibm_result, tuple):
        ibm_works, ibm_channel = ibm_result
    else:
        ibm_works, ibm_channel = ibm_result, None
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)
    
    print(f"OpenAI API:     {'✅ Working' if openai_works else '❌ Needs Fix'}")
    print(f"IBM Quantum:    {'✅ Working' if ibm_works else '❌ Needs Fix'}")
    
    if ibm_works:
        print(f"IBM Channel:    {ibm_channel}")
    
    # Create template
    create_working_env_template(openai_works, ibm_works, ibm_channel)
    
    # Final recommendations
    print("\n🎯 NEXT STEPS:")
    if openai_works and ibm_works:
        print("🎉 Both APIs are working! Your quantum MCP server should work perfectly.")
        print("   Run: python client.py demo")
    elif openai_works and not ibm_works:
        print("🔄 OpenAI works, but fix IBM Quantum token for hardware access.")
        print("   Server will work with simulator until IBM is fixed.")
    elif not openai_works and ibm_works:
        print("🔄 IBM Quantum works, but fix OpenAI key for better query processing.")
        print("   Server will work but use local query processing.")
    else:
        print("🔧 Both APIs need fixing. Start with getting new tokens.")
        print("   Server will work with simulator + local processing as fallback.")

if __name__ == "__main__":
    main()