#!/usr/bin/env python3
"""
Test script to check if environment variables are being read correctly
"""

import os

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Successfully loaded .env file using python-dotenv")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# Manual .env file reading
def read_env_manually():
    """Read .env file manually"""
    env_vars = {}
    try:
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                print("📄 Reading .env file manually...")
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
                            print(f"   Line {line_num}: {key.strip()}={value.strip()[:8]}...")
            return env_vars
        else:
            print("❌ No .env file found in current directory")
            return {}
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return {}

def check_api_keys():
    """Check API keys from all sources"""
    print("🔍 Checking API Keys")
    print("=" * 50)
    
    # Check environment variables
    openai_env = os.getenv('OPENAI_API_KEY')
    ibm_env = os.getenv('IBM_QUANTUM_TOKEN')
    
    print("Environment Variables:")
    if openai_env:
        print(f"  ✅ OPENAI_API_KEY: {openai_env[:8]}...")
    else:
        print("  ❌ OPENAI_API_KEY: Not found")
    
    if ibm_env:
        print(f"  ✅ IBM_QUANTUM_TOKEN: {ibm_env[:8]}...")
    else:
        print("  ❌ IBM_QUANTUM_TOKEN: Not found")
    
    # Check .env file manually
    print("\n.env File Contents:")
    env_vars = read_env_manually()
    
    openai_file = env_vars.get('OPENAI_API_KEY')
    ibm_file = env_vars.get('IBM_QUANTUM_TOKEN')
    
    if openai_file:
        print(f"  ✅ OPENAI_API_KEY: {openai_file[:8]}...")
    else:
        print("  ❌ OPENAI_API_KEY: Not found in .env")
    
    if ibm_file:
        print(f"  ✅ IBM_QUANTUM_TOKEN: {ibm_file[:8]}...")
    else:
        print("  ❌ IBM_QUANTUM_TOKEN: Not found in .env")
    
    # Final status
    print(f"\n📊 Summary:")
    if openai_env or openai_file:
        print("  ✅ OpenAI API key available")
    else:
        print("  ❌ OpenAI API key missing")
    
    if ibm_env or ibm_file:
        print("  ✅ IBM Quantum token available")
    else:
        print("  ❌ IBM Quantum token missing")

def create_sample_env():
    """Create a sample .env file"""
    print("\n🔧 Creating sample .env file...")
    
    sample_content = """# Quantum MCP Server Environment Variables
# Replace the values below with your actual API keys

OPENAI_API_KEY=sk-proj-your-openai-api-key-here
IBM_QUANTUM_TOKEN=your-ibm-quantum-token-here

# Optional settings
LOG_LEVEL=INFO
DEFAULT_SHOTS=1024
"""
    
    try:
        if os.path.exists('.env'):
            backup_name = '.env.backup'
            print(f"  📁 Backing up existing .env to {backup_name}")
            os.rename('.env', backup_name)
        
        with open('.env', 'w') as f:
            f.write(sample_content)
        
        print("  ✅ Created sample .env file")
        print("  📝 Edit .env file and add your actual API keys")
        
    except Exception as e:
        print(f"  ❌ Error creating .env file: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'create':
        create_sample_env()
    else:
        check_api_keys()
        
        if not os.path.exists('.env'):
            response = input("\n🤔 Create sample .env file? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                create_sample_env()