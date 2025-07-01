#!/usr/bin/env python3
"""
Check and fix token configuration for Claude Desktop
"""

import json
import os
from pathlib import Path
import platform

def get_claude_config_path():
    """Get Claude Desktop config path"""
    if platform.system() == "Windows":
        appdata = os.getenv('APPDATA')
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
        else:
            return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif platform.system() == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"

def get_api_keys_from_env():
    """Get API keys from .env file"""
    def get_key(key_name):
        # Environment
        value = os.getenv(key_name)
        if value:
            return value
        
        # .env file
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            if '=' in line:
                                env_key, env_value = line.strip().split('=', 1)
                                if env_key.strip() == key_name:
                                    # Remove quotes if present
                                    env_value = env_value.strip().strip('"').strip("'")
                                    return env_value
        except Exception as e:
            print(f"Error reading .env: {e}")
        
        return None
    
    return get_key('OPENAI_API_KEY'), get_key('IBM_QUANTUM_TOKEN')

def check_claude_config():
    """Check current Claude Desktop configuration"""
    print("🔍 Checking Claude Desktop Configuration")
    print("=" * 50)
    
    config_path = get_claude_config_path()
    print(f"Config file: {config_path}")
    
    if not config_path.exists():
        print("❌ Claude config file doesn't exist!")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "mcpServers" not in config:
            print("❌ No mcpServers section found")
            return config
        
        if "quantum-computation" not in config["mcpServers"]:
            print("❌ quantum-computation server not found")
            return config
        
        server_config = config["mcpServers"]["quantum-computation"]
        print("✅ Found quantum-computation server")
        
        # Check environment variables
        if "env" in server_config:
            env_vars = server_config["env"]
            
            openai_key = env_vars.get("OPENAI_API_KEY", "")
            ibm_token = env_vars.get("IBM_QUANTUM_TOKEN", "")
            
            print(f"\n🔑 Configured API Keys:")
            
            # Check OpenAI key
            if openai_key:
                if openai_key.startswith("sk-") and len(openai_key) > 20:
                    print(f"✅ OpenAI API Key: {openai_key[:8]}...{openai_key[-4:]} (looks valid)")
                elif openai_key in ["your-openai-api-key-here", "your-key-here"]:
                    print(f"❌ OpenAI API Key: PLACEHOLDER - needs real key!")
                else:
                    print(f"⚠️  OpenAI API Key: {openai_key[:8]}... (check format)")
            else:
                print(f"❌ OpenAI API Key: MISSING")
            
            # Check IBM token
            if ibm_token:
                if len(ibm_token) > 50:
                    print(f"✅ IBM Quantum Token: {ibm_token[:8]}...{ibm_token[-4:]} (looks valid)")
                elif ibm_token in ["your-ibm-quantum-token-here", "your-token-here"]:
                    print(f"❌ IBM Quantum Token: PLACEHOLDER - needs real token!")
                else:
                    print(f"⚠️  IBM Quantum Token: {ibm_token[:8]}... (check format)")
            else:
                print(f"❌ IBM Quantum Token: MISSING")
                
        else:
            print("❌ No environment variables configured")
        
        return config
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return None

def fix_claude_config():
    """Fix Claude config with real API keys"""
    print("\n🔧 Fixing Claude Configuration")
    print("=" * 50)
    
    # Get real API keys
    openai_key, ibm_token = get_api_keys_from_env()
    
    if not openai_key:
        print("❌ OpenAI API key not found in .env file")
        return False
    
    if not ibm_token:
        print("❌ IBM Quantum token not found in .env file")
        return False
    
    print(f"✅ Found API keys in .env file:")
    print(f"   OpenAI: {openai_key[:8]}...{openai_key[-4:]}")
    print(f"   IBM: {ibm_token[:8]}...{ibm_token[-4:]}")
    
    # Get Claude config
    config_path = get_claude_config_path()
    
    # Read existing config
    config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except:
            pass
    
    # Update config
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Get current paths
    python_path = "D:/Coding_sakshi/mcp/QuantumCompute_mcp_server/.venv/Scripts/python.exe"
    server_path = "D:/Coding_sakshi/mcp/QuantumCompute_mcp_server/server.py"
    
    # Update quantum-computation server
    config["mcpServers"]["quantum-computation"] = {
        "command": python_path,
        "args": [server_path],
        "env": {
            "OPENAI_API_KEY": openai_key,
            "IBM_QUANTUM_TOKEN": ibm_token
        }
    }
    
    # Write config
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated Claude config with real API keys")
        return True
        
    except Exception as e:
        print(f"❌ Error writing config: {e}")
        return False

def main():
    """Main function"""
    print("🔑 Claude Desktop Token Configuration Checker")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Make sure you're in the QuantumCompute_mcp_server directory")
        return False
    
    # Check current config
    current_config = check_claude_config()
    
    if current_config is None:
        print("\n❌ Could not read Claude config")
        return False
    
    # Check .env file
    print(f"\n📄 Checking .env file...")
    openai_key, ibm_token = get_api_keys_from_env()
    
    if openai_key and ibm_token:
        print(f"✅ Found valid API keys in .env:")
        print(f"   OpenAI: {openai_key[:8]}...{openai_key[-4:]}")
        print(f"   IBM: {ibm_token[:8]}...{ibm_token[-4:]}")
        
        # Offer to fix config
        response = input(f"\n🤔 Update Claude config with these real tokens? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            if fix_claude_config():
                print(f"\n🎉 Configuration fixed!")
                print(f"\n🔄 Next steps:")
                print(f"1. Restart Claude Desktop completely")
                print(f"2. Ask Claude: 'Create a Bell state'")
                print(f"3. It should now use your real API tokens!")
                return True
        else:
            print(f"\n💡 Manual fix:")
            print(f"   Replace placeholder tokens in Claude config with:")
            print(f"   OPENAI_API_KEY: {openai_key}")
            print(f"   IBM_QUANTUM_TOKEN: {ibm_token}")
    else:
        print(f"❌ API keys not found in .env file")
        print(f"   Add them to .env file first")
    
    return False

if __name__ == "__main__":
    main()