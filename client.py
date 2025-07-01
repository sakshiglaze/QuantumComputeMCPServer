#!/usr/bin/env python3
"""
Quantum MCP Client Example
Demonstrates how to interact with the Quantum Computation MCP Server
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Dict, Any

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("📄 Loaded .env file")
except ImportError:
    print("💡 Install python-dotenv to use .env files: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️  MCP library not available, using subprocess mode only")
    MCP_AVAILABLE = False

class QuantumMCPClient:
    """Client for interacting with Quantum MCP Server"""
    
    def __init__(self):
        self.session = None
        self.stdio_context = None
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.ibm_token = os.getenv('IBM_QUANTUM_TOKEN')
    
    async def connect(self, server_path: str = "./server.py"):
        """Connect to the MCP server"""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[server_path],
                env=os.environ.copy()
            )
            
            # Start the server process and create session
            stdio_transport = await stdio_client(server_params)
            self.session = ClientSession(stdio_transport[0], stdio_transport[1])
            
            # Initialize the session
            await self.session.initialize()
            
            print("✅ Connected to Quantum MCP Server")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            print(f"   Make sure the server file exists at: {server_path}")
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        try:
            if self.session:
                await self.session.close()
            print("🔌 Disconnected from server")
        except Exception as e:
            print(f"⚠️  Error during disconnect: {e}")
    
    async def list_tools(self):
        """List available tools"""
        try:
            tools = await self.session.list_tools()
            print("\n🛠️  Available Tools:")
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description}")
            return tools.tools
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return []
    
    async def run_quantum_computation(self, query: str, shots: int = 1024):
        """Run a quantum computation"""
        if not self.openai_key or not self.ibm_token:
            print("❌ Please set OPENAI_API_KEY and IBM_QUANTUM_TOKEN environment variables")
            return None
        
        try:
            print(f"\n🚀 Running quantum computation: '{query}'")
            print("⏳ Processing...")
            
            result = await self.session.call_tool(
                "quantum_compute",
                {
                    "query": query,
                    "openai_key": self.openai_key,
                    "ibm_token": self.ibm_token,
                    "shots": shots
                }
            )
            
            if hasattr(result, 'isError') and result.isError:
                print(f"❌ Error: {result.content[0].text}")
                return None
            
            print("\n" + "="*50)
            if hasattr(result, 'content') and result.content:
                print(result.content[0].text)
            else:
                print("No content returned from server")
            print("="*50)
            return result
        except Exception as e:
            print(f"❌ Error running computation: {e}")
            return None
    
    async def list_backends(self):
        """List available quantum backends"""
        if not self.ibm_token:
            print("❌ Please set IBM_QUANTUM_TOKEN environment variable")
            return None
        
        try:
            print("\n📡 Fetching available quantum backends...")
            
            result = await self.session.call_tool(
                "list_quantum_backends",
                {"ibm_token": self.ibm_token}
            )
            
            if hasattr(result, 'isError') and result.isError:
                print(f"❌ Error: {result.content[0].text}")
                return None
            
            if hasattr(result, 'content') and result.content:
                print(result.content[0].text)
            return result
        except Exception as e:
            print(f"❌ Error listing backends: {e}")
            return None
    
    async def get_circuit_info(self, operation: str):
        """Get information about a quantum operation"""
        try:
            print(f"\n📚 Getting information about '{operation}'...")
            
            result = await self.session.call_tool(
                "quantum_circuit_info",
                {"operation": operation}
            )
            
            if hasattr(result, 'isError') and result.isError:
                print(f"❌ Error: {result.content[0].text}")
                return None
            
            print(f"\nℹ️  {operation.upper()}:")
            if hasattr(result, 'content') and result.content:
                print(result.content[0].text)
            return result
        except Exception as e:
            print(f"❌ Error getting circuit info: {e}")
            return None


# Alternative simplified client using subprocess
class SimpleQuantumClient:
    """Simplified client using subprocess communication"""
    
    def __init__(self):
        # Use the same API key reading method
        self.openai_key = self._get_api_key('OPENAI_API_KEY')
        self.ibm_token = self._get_api_key('IBM_QUANTUM_TOKEN')
    
    def _get_api_key(self, key_name):
        """Get API key from environment or .env file"""
        # First try environment variable
        value = os.getenv(key_name)
        if value:
            return value
        
        # Try reading from .env file manually if dotenv failed
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            if '=' in line:
                                env_key, env_value = line.strip().split('=', 1)
                                if env_key.strip() == key_name:
                                    return env_value.strip()
        except Exception as e:
            print(f"⚠️  Error reading .env file: {e}")
        
        return None
    
    async def run_computation(self, query: str, shots: int = 1024):
        """Run a quantum computation using subprocess"""
        if not self.openai_key or not self.ibm_token:
            print("❌ API keys not found!")
            print("   Run: python client.py keys")
            return None
        
        try:
            print(f"\n🚀 Running quantum computation: '{query}'")
            print("⏳ Processing...")
            
            # Start server process with environment variables
            env = os.environ.copy()
            env['OPENAI_API_KEY'] = self.openai_key
            env['IBM_QUANTUM_TOKEN'] = self.ibm_token
            
            process = subprocess.Popen(
                [sys.executable, "server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',  # Handle encoding errors gracefully
                env=env
            )
            
            try:
                # Step 1: Send initialization request
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "quantum-client",
                            "version": "1.0.0"
                        }
                    }
                }
                
                process.stdin.write(json.dumps(init_request) + "\n")
                process.stdin.flush()
                
                # Step 2: Wait for initialization response
                await asyncio.sleep(2)
                
                # Step 3: Send initialized notification
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                process.stdin.write(json.dumps(initialized_notification) + "\n")
                process.stdin.flush()
                
                # Step 4: Send tool call request
                tool_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "quantum_compute",
                        "arguments": {
                            "query": query,
                            "openai_key": self.openai_key,
                            "ibm_token": self.ibm_token,
                            "shots": shots
                        }
                    }
                }
                
                process.stdin.write(json.dumps(tool_request) + "\n")
                process.stdin.flush()
                process.stdin.close()
                
                # Step 5: Wait for response with timeout
                stdout, stderr = process.communicate(timeout=120)
                
                print("\n" + "="*50)
                if stdout:
                    print("📤 Server Response:")
                    # Parse JSON responses line by line
                    lines = stdout.strip().split('\n')
                    quantum_result_found = False
                    
                    for line in lines:
                        if line.strip():
                            try:
                                response = json.loads(line)
                                
                                # Look for tool call response
                                if 'result' in response and response.get('id') == 2:
                                    result_data = response['result']
                                    if isinstance(result_data, list) and len(result_data) > 0:
                                        # Extract text content from response
                                        content_item = result_data[0]
                                        if isinstance(content_item, dict) and content_item.get('type') == 'text':
                                            print(content_item['text'])
                                            quantum_result_found = True
                                        else:
                                            print(json.dumps(result_data, indent=2))
                                            quantum_result_found = True
                                    else:
                                        print(f"📋 Server response: {json.dumps(result_data, indent=2)}")
                                
                                # Handle errors
                                elif 'error' in response:
                                    print(f"❌ Server Error: {response['error']['message']}")
                                    if 'data' in response['error']:
                                        print(f"   Details: {response['error']['data']}")
                                
                                # Handle initialization response
                                elif 'result' in response and response.get('id') == 1:
                                    server_info = response['result'].get('serverInfo', {})
                                    print(f"🔗 Connected to {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
                                
                            except json.JSONDecodeError:
                                # Non-JSON output, probably logs
                                if line.strip() and not line.startswith('INFO:') and not line.startswith('WARNING:'):
                                    print(f"📝 {line}")
                    
                    if not quantum_result_found:
                        print("⚠️  No quantum computation result found in server response")
                        print("🔍 Full server output:")
                        print(stdout)
                else:
                    print("❌ No output received from server")
                
                if stderr and stderr.strip():
                    # Filter out routine log messages
                    error_lines = []
                    for line in stderr.split('\n'):
                        if line.strip() and not any(x in line for x in ['INFO:', 'Services initialized successfully']):
                            error_lines.append(line)
                    
                    if error_lines:
                        print("\n⚠️  Server Messages:")
                        for line in error_lines:
                            print(f"   {line}")
                
                print("="*50)
                
                return stdout
                
            except subprocess.TimeoutExpired:
                process.kill()
                print("❌ Server timed out after 120 seconds")
                return None
            
        except Exception as e:
            print(f"❌ Error running computation: {e}")
            return None


async def demo_quantum_computations():
    """Demonstrate various quantum computations"""
    
    # Try MCP client first, but always fall back to simple client
    if MCP_AVAILABLE:
        client = QuantumMCPClient()
        if await client.connect():
            print("🎯 Using MCP client mode")
            try:
                # List available tools
                await client.list_tools()
                
                # List available backends
                await client.list_backends()
                
                # Get information about operations
                operations = ["bell_state", "grover", "qft", "teleportation"]
                for op in operations:
                    await client.get_circuit_info(op)
                
                # Run various quantum computations
                queries = [
                    "Create a Bell state to demonstrate quantum entanglement",
                    "Generate quantum random numbers using 3 qubits", 
                    "Run Grover's algorithm to search for a marked item",
                    "Apply quantum Fourier transform on 3 qubits",
                    "Demonstrate quantum superposition with Hadamard gates"
                ]
                
                for query in queries:
                    await client.run_quantum_computation(query, shots=1024)
                    await asyncio.sleep(2)  # Brief pause between computations
                
                await client.disconnect()
                return
                
            except Exception as e:
                print(f"⚠️  MCP client error during demo: {e}")
                await client.disconnect()
    
    # Fallback to simple client
    print("🔄 Using subprocess client mode")
    simple_client = SimpleQuantumClient()
    
    # Check API keys
    if not simple_client.openai_key or not simple_client.ibm_token:
        print("❌ API keys not found!")
        print("   Run: python client.py keys")
        return
    
    # Run one test with simple client
    await simple_client.run_computation("Create a Bell state to demonstrate quantum entanglement")
    await simple_client.run_computation("Generate quantum random numbers using 3 qubits")


async def interactive_mode():
    """Interactive mode for custom queries"""
    client = QuantumMCPClient()
    
    if not await client.connect():
        print("\n⚠️  MCP client failed, using simple mode...")
        simple_client = SimpleQuantumClient()
        
        print("\n🎮 Simple Interactive Quantum Computation Mode")
        print("Type 'quit' to exit")
        
        while True:
            query = input("\n🔬 Enter quantum computation query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            else:
                await simple_client.run_computation(query)
        return
    
    print("\n🎮 Interactive Quantum Computation Mode")
    print("Type 'help' for available commands, 'quit' to exit")
    
    try:
        while True:
            query = input("\n🔬 Enter quantum computation query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            elif query.lower() == 'help':
                print("""
Available commands:
• 'list tools' - Show available tools
• 'list backends' - Show quantum backends  
• 'info <operation>' - Get info about operation
• Any natural language quantum query
• 'quit' - Exit

Example queries:
• "Create a Bell state"
• "Run Grover search on 4 qubits"
• "Generate quantum random bits"
• "Apply QFT to 3 qubits"
                """)
            elif query.lower() == 'list tools':
                await client.list_tools()
            elif query.lower() == 'list backends':
                await client.list_backends()
            elif query.lower().startswith('info '):
                operation = query[5:].strip()
                await client.get_circuit_info(operation)
            else:
                await client.run_quantum_computation(query)
    
    finally:
        await client.disconnect()


# Test server connectivity
async def test_server():
    """Test if the server is working"""
    print("🧪 Testing server connectivity...")
    
    try:
        # Test simple subprocess connection
        process = subprocess.Popen(
            [sys.executable, "server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send a simple request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait briefly
        await asyncio.sleep(2)
        
        # Check if process is responsive
        if process.poll() is None:
            print("✅ Server is running and responsive!")
            process.terminate()
            await asyncio.sleep(1)
            if process.poll() is None:
                process.kill()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False


# Claude Desktop Configuration
def generate_claude_config():
    """Generate Claude Desktop configuration"""
    # Get absolute path to server
    server_path = os.path.abspath("server.py")
    
    config = {
        "mcpServers": {
            "quantum-computation": {
                "command": "python",
                "args": [server_path],
                "env": {
                    "OPENAI_API_KEY": "your-openai-api-key-here",
                    "IBM_QUANTUM_TOKEN": "your-ibm-quantum-token-here"
                }
            }
        }
    }
    
    return json.dumps(config, indent=2)


def save_claude_config():
    """Save Claude Desktop configuration"""
    config_content = generate_claude_config()
    
    # Determine config path based on OS
    import platform
    system = platform.system()
    
    if system == "Darwin":  # macOS
        config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    elif system == "Windows":
        config_path = os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json")
    else:  # Linux
        config_path = os.path.expanduser("~/.config/claude/claude_desktop_config.json")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Read existing config if it exists
    existing_config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
        except:
            pass
    
    # Merge configurations
    new_config = json.loads(config_content)
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"].update(new_config["mcpServers"])
    
    # Write configuration
    with open(config_path, 'w') as f:
        f.write(json.dumps(existing_config, indent=2))
    
    print(f"📝 Claude configuration saved to: {config_path}")
    print("⚠️  Remember to update the API keys in the configuration file!")
    print(f"🔧 Server path set to: {os.path.abspath('server.py')}")


def setup_api_keys():
    """Helper function to set up API keys"""
    print("🔑 API Key Setup")
    print("=" * 50)
    
    # Try different methods to get API keys
    def get_api_key(key_name):
        # Environment variable
        value = os.getenv(key_name)
        if value:
            return value, "environment"
        
        # .env file
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            if '=' in line:
                                env_key, env_value = line.strip().split('=', 1)
                                if env_key.strip() == key_name:
                                    return env_value.strip(), ".env file"
        except Exception:
            pass
        
        return None, "not found"
    
    openai_key, openai_source = get_api_key('OPENAI_API_KEY')
    ibm_token, ibm_source = get_api_key('IBM_QUANTUM_TOKEN')
    
    if openai_key:
        print(f"✅ OPENAI_API_KEY found in {openai_source}: {openai_key[:8]}...")
    else:
        print("❌ OPENAI_API_KEY not found")
    
    if ibm_token:
        print(f"✅ IBM_QUANTUM_TOKEN found in {ibm_source}: {ibm_token[:8]}...")
    else:
        print("❌ IBM_QUANTUM_TOKEN not found")
    
    if not openai_key or not ibm_token:
        print("\n📋 How to set API keys:")
        print("\n🔧 Option 1 - Environment Variables:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("   export IBM_QUANTUM_TOKEN='your-token-here'")
        
        print("\n📄 Option 2 - Create .env file:")
        print("   Create a file named '.env' in this directory with:")
        print("   OPENAI_API_KEY=your-key-here")
        print("   IBM_QUANTUM_TOKEN=your-token-here")
        
        print("\n💡 Option 3 - Use setup script:")
        print("   python setup_env.py")
        
        print("\n🌐 Get your API keys from:")
        print("   • OpenAI: https://platform.openai.com/api-keys")
        print("   • IBM Quantum: https://quantum-computing.ibm.com/account")
        
        # Offer to create .env file
        if not os.path.exists('.env'):
            response = input("\n🤔 Create .env file now? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return create_env_file_interactive()
        
        return False
    
    return True

def create_env_file_interactive():
    """Create .env file interactively"""
    print("\n📄 Creating .env file...")
    
    openai_key = input("Enter your OpenAI API key: ").strip()
    if not openai_key:
        print("❌ OpenAI API key is required!")
        return False
    
    ibm_token = input("Enter your IBM Quantum token: ").strip()
    if not ibm_token:
        print("❌ IBM Quantum token is required!")
        return False
    
    try:
        env_content = f"""# Quantum MCP Server Environment Variables
OPENAI_API_KEY={openai_key}
IBM_QUANTUM_TOKEN={ibm_token}

# Optional settings
LOG_LEVEL=INFO
DEFAULT_SHOTS=1024
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file!")
        print("🔄 Restart the client to use the new keys")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False
def main():
    """Main function with CLI interface"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'demo':
            print("🎯 Running quantum computation demo...")
            asyncio.run(demo_quantum_computations())
        elif command == 'interactive':
            print("🎮 Starting interactive mode...")
            asyncio.run(interactive_mode())
        elif command == 'config':
            print("⚙️  Generating Claude Desktop configuration...")
            save_claude_config()
        elif command == 'test':
            print("🧪 Testing server...")
            asyncio.run(test_server())
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: demo, interactive, config, test")
    else:
        print("""
🚀 Quantum MCP Client

Usage:
  python client.py demo        # Run demonstration
  python client.py interactive # Interactive mode  
  python client.py config      # Generate Claude config
  python client.py test        # Test server connectivity

Environment Variables:
  OPENAI_API_KEY     - Your OpenAI API key
  IBM_QUANTUM_TOKEN  - Your IBM Quantum token
        """)


if __name__ == "__main__":
    main()


# Example usage in other Python code
"""
async def example_usage():
    client = QuantumMCPClient()
    await client.connect()
    
    # Run a quantum computation
    result = await client.run_quantum_computation(
        "Create a 3-qubit GHZ state",
        shots=2048
    )
    
    await client.disconnect()

# Run the example
# asyncio.run(example_usage())
"""