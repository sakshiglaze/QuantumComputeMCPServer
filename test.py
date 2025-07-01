#!/usr/bin/env python3
"""
Test Suite and Deployment Scripts for Quantum MCP Server
"""

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, AsyncMock
import sys
import subprocess

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quantum_mcp_server import QuantumMCPServer, QuantumOperationType, QuantumComputationRequest


class TestQuantumMCPServer(unittest.TestCase):
    """Test cases for Quantum MCP Server"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.server = QuantumMCPServer()
        self.mock_openai_key = "test-openai-key"
        self.mock_ibm_token = "test-ibm-token"
    
    def test_server_initialization(self):
        """Test server initialization"""
        self.assertIsNotNone(self.server.server)
        self.assertEqual(self.server.server.name, "quantum-computation")
    
    @patch('quantum_mcp_server.openai.OpenAI')
    @patch('quantum_mcp_server.QiskitRuntimeService')
    def test_service_initialization(self, mock_qiskit, mock_openai):
        """Test service initialization with mocked services"""
        result = self.server.initialize_services(
            self.mock_openai_key, 
            self.mock_ibm_token
        )
        self.assertTrue(result)
        mock_openai.assert_called_once_with(api_key=self.mock_openai_key)
    
    def test_quantum_computation_request_creation(self):
        """Test quantum computation request creation"""
        request = QuantumComputationRequest(
            query="Create a Bell state",
            operation_type=QuantumOperationType.BELL_STATE,
            parameters={},
            num_qubits=2
        )
        
        self.assertEqual(request.query, "Create a Bell state")
        self.assertEqual(request.operation_type, QuantumOperationType.BELL_STATE)
        self.assertEqual(request.num_qubits, 2)
    
    def test_bell_state_circuit_creation(self):
        """Test Bell state circuit creation"""
        request = QuantumComputationRequest(
            query="Create a Bell state",
            operation_type=QuantumOperationType.BELL_STATE,
            parameters={},
            num_qubits=2
        )
        
        circuit = self.server.create_quantum_circuit(request)
        
        # Check circuit properties
        self.assertEqual(circuit.num_qubits, 2)
        self.assertEqual(circuit.num_clbits, 2)
        
        # Check gates (Hadamard + CNOT for Bell state)
        gates = [instruction.operation.name for instruction, _, _ in circuit.data]
        self.assertIn('h', gates)  # Hadamard gate
        self.assertIn('cx', gates)  # CNOT gate
    
    def test_quantum_random_circuit_creation(self):
        """Test quantum random number generator circuit"""
        request = QuantumComputationRequest(
            query="Generate random numbers",
            operation_type=QuantumOperationType.QUANTUM_RANDOM,
            parameters={},
            num_qubits=3
        )
        
        circuit = self.server.create_quantum_circuit(request)
        
        # Check circuit properties
        self.assertEqual(circuit.num_qubits, 3)
        
        # Check that Hadamard gates are applied to all qubits
        gates = [instruction.operation.name for instruction, _, _ in circuit.data]
        hadamard_count = gates.count('h')
        self.assertEqual(hadamard_count, 3)
    
    @patch('quantum_mcp_server.openai.OpenAI')
    async def test_openai_query_processing(self, mock_openai):
        """Test OpenAI query processing"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "operation_type": "bell_state",
            "num_qubits": 2,
            "parameters": {},
            "reasoning": "User wants to create entangled qubits"
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        self.server.openai_client = mock_client
        
        result = await self.server.process_query_with_openai("Create a Bell state")
        
        self.assertEqual(result.operation_type, QuantumOperationType.BELL_STATE)
        self.assertEqual(result.num_qubits, 2)
    
    def test_result_formatting(self):
        """Test result formatting"""
        request = QuantumComputationRequest(
            query="Test query",
            operation_type=QuantumOperationType.BELL_STATE,
            parameters={},
            num_qubits=2
        )
        
        circuit = self.server.create_quantum_circuit(request)
        
        results = {
            "backend": "test_backend",
            "shots": 1024,
            "counts": {"00": 512, "11": 512},
            "circuit_depth": 2,
            "circuit_width": 2
        }
        
        formatted = self.server.format_results(request, circuit, results)
        
        # Check that key information is included
        self.assertIn("Test query", formatted)
        self.assertIn("bell_state", formatted)
        self.assertIn("test_backend", formatted)
        self.assertIn("00", formatted)
        self.assertIn("11", formatted)


class TestQuantumOperations(unittest.TestCase):
    """Test specific quantum operations"""
    
    def setUp(self):
        self.server = QuantumMCPServer()
    
    def test_all_operation_types(self):
        """Test all supported operation types"""
        operations = [
            (QuantumOperationType.BELL_STATE, 2),
            (QuantumOperationType.QUANTUM_FOURIER_TRANSFORM, 3),
            (QuantumOperationType.GROVER_SEARCH, 3),
            (QuantumOperationType.QUANTUM_RANDOM, 4),
            (QuantumOperationType.DEUTSCH_JOZSA, 3),
        ]
        
        for op_type, num_qubits in operations:
            request = QuantumComputationRequest(
                query=f"Test {op_type.value}",
                operation_type=op_type,
                parameters={},
                num_qubits=num_qubits
            )
            
            circuit = self.server.create_quantum_circuit(request)
            
            # Basic checks
            self.assertEqual(circuit.num_qubits, num_qubits)
            self.assertGreater(len(circuit.data), 0)  # Circuit should have gates


class IntegrationTest(unittest.TestCase):
    """Integration tests with mocked external services"""
    
    @patch('quantum_mcp_server.QiskitRuntimeService')
    @patch('quantum_mcp_server.openai.OpenAI')
    async def test_full_computation_flow(self, mock_openai, mock_qiskit):
        """Test complete computation flow with mocked services"""
        # Mock OpenAI
        mock_openai_response = Mock()
        mock_openai_response.choices = [Mock()]
        mock_openai_response.choices[0].message.content = json.dumps({
            "operation_type": "bell_state",
            "num_qubits": 2,
            "parameters": {},
            "reasoning": "Bell state requested"
        })
        
        mock_openai_client = Mock()
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        mock_openai.return_value = mock_openai_client
        
        # Mock IBM Quantum
        mock_backend = Mock()
        mock_backend.name = "test_backend"
        mock_backend.configuration.return_value.num_qubits = 5
        mock_backend.configuration.return_value.simulator = False
        
        mock_service = Mock()
        mock_service.least_busy.return_value = mock_backend
        mock_qiskit.return_value = mock_service
        
        # Mock job results
        mock_result = Mock()
        mock_result.get_counts.return_value = {"00": 500, "11": 524}
        
        server = QuantumMCPServer()
        server.openai_client = mock_openai_client
        server.ibm_service = mock_service
        
        # Process query
        request = await server.process_query_with_openai("Create a Bell state")
        
        # Create circuit
        circuit = server.create_quantum_circuit(request)
        
        # Verify results
        self.assertEqual(request.operation_type, QuantumOperationType.BELL_STATE)
        self.assertEqual(circuit.num_qubits, 2)


# Performance and Load Testing
class PerformanceTest(unittest.TestCase):
    """Performance and load testing"""
    
    def test_circuit_creation_performance(self):
        """Test circuit creation performance"""
        import time
        
        server = QuantumMCPServer()
        
        operations = [
            QuantumOperationType.BELL_STATE,
            QuantumOperationType.QUANTUM_RANDOM,
            QuantumOperationType.QUANTUM_FOURIER_TRANSFORM
        ]
        
        for op_type in operations:
            start_time = time.time()
            
            for _ in range(100):  # Create 100 circuits
                request = QuantumComputationRequest(
                    query="Performance test",
                    operation_type=op_type,
                    parameters={},
                    num_qubits=3
                )
                circuit = server.create_quantum_circuit(request)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should create 100 circuits in under 1 second
            self.assertLess(duration, 1.0, 
                           f"{op_type.value} circuit creation too slow: {duration}s")


# Deployment and Setup Scripts
class DeploymentScripts:
    """Scripts for deployment and setup"""
    
    @staticmethod
    def create_docker_file():
        """Create Dockerfile for containerized deployment"""
        dockerfile_content = """
# Dockerfile for Quantum MCP Server
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY quantum_mcp_server.py .
COPY quantum_mcp_client.py .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose MCP port (if needed)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import quantum_mcp_server; print('OK')" || exit 1

# Run the server
CMD ["python", "quantum_mcp_server.py"]
        """
        
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content.strip())
        print("✅ Dockerfile created")
    
    @staticmethod
    def create_docker_compose():
        """Create docker-compose.yml for easy deployment"""
        compose_content = """
version: '3.8'

services:
  quantum-mcp-server:
    build: .
    container_name: quantum-mcp-server
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - IBM_QUANTUM_TOKEN=${IBM_QUANTUM_TOKEN}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - quantum-network

networks:
  quantum-network:
    driver: bridge

volumes:
  quantum-data:
        """
        
        with open("docker-compose.yml", "w") as f:
            f.write(compose_content.strip())
        print("✅ docker-compose.yml created")
    
    @staticmethod
    def create_env_template():
        """Create environment template file"""
        env_content = """
# Quantum MCP Server Environment Variables
# Copy this file to .env and fill in your actual values

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# IBM Quantum Configuration  
IBM_QUANTUM_TOKEN=your-ibm-quantum-token-here
IBM_QUANTUM_BACKEND=ibm_brisbane

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/quantum-mcp.log

# Performance Configuration
DEFAULT_SHOTS=1024
MAX_QUBITS=10
CIRCUIT_TIMEOUT=300

# Security Configuration
ALLOWED_HOSTS=localhost,127.0.0.1
API_RATE_LIMIT=100
        """
        
        with open(".env.template", "w") as f:
            f.write(env_content.strip())
        print("✅ .env.template created")
    
    @staticmethod
    def setup_development_environment():
        """Setup development environment"""
        commands = [
            "python -m venv venv",
            "source venv/bin/activate" if os.name != 'nt' else "venv\\Scripts\\activate",
            "pip install --upgrade pip",
            "pip install -r requirements.txt",
            "pip install -e .",
            "pre-commit install"  # If using pre-commit hooks
        ]
        
        print("🔧 Development Environment Setup Commands:")
        for cmd in commands:
            print(f"  {cmd}")
        
        # Create pre-commit configuration
        precommit_content = """
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
        """
        
        with open(".pre-commit-config.yaml", "w") as f:
            f.write(precommit_content.strip())
        print("✅ .pre-commit-config.yaml created")


def run_tests():
    """Run all tests"""
    print("🧪 Running Quantum MCP Server Tests...")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='*test*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
    
    return result.wasSuccessful()


def setup_project():
    """Setup the complete project structure"""
    print("🚀 Setting up Quantum MCP Server project...")
    
    # Create deployment files
    DeploymentScripts.create_docker_file()
    DeploymentScripts.create_docker_compose()
    DeploymentScripts.create_env_template()
    DeploymentScripts.setup_development_environment()
    
    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("tests", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    print("\n📁 Project structure created:")
    print("  ├── quantum_mcp_server.py")
    print("  ├── quantum_mcp_client.py")
    print("  ├── requirements.txt")
    print("  ├── setup.py")
    print("  ├── Dockerfile")
    print("  ├── docker-compose.yml")
    print("  ├── .env.template")
    print("  ├── .pre-commit-config.yaml")
    print("  ├── logs/")
    print("  ├── tests/")
    print("  └── docs/")
    
    print("\n✅ Project setup complete!")
    print("\n📋 Next steps:")
    print("  1. Copy .env.template to .env and add your API keys")
    print("  2. Run: pip install -r requirements.txt")
    print("  3. Run tests: python quantum_mcp_tests.py test")
    print("  4. Start server: python quantum_mcp_server.py")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            success = run_tests()
            sys.exit(0 if success else 1)
        elif command == "setup":
            setup_project()
        elif command == "docker":
            DeploymentScripts.create_docker_file()
            DeploymentScripts.create_docker_compose()
        elif command == "env":
            DeploymentScripts.create_env_template()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: test, setup, docker, env")
    else:
        print("""
🧪 Quantum MCP Server Testing & Deployment

Commands:
  python quantum_mcp_tests.py test    # Run all tests
  python quantum_mcp_tests.py setup   # Setup project structure
  python quantum_mcp_tests.py docker  # Create Docker files
  python quantum_mcp_tests.py env     # Create environment template
        """)


# Run async tests
async def run_async_tests():
    """Run async test cases"""
    test_cases = [
        TestQuantumMCPServer(),
        IntegrationTest()
    ]
    
    for test_case in test_cases:
        if hasattr(test_case, 'test_openai_query_processing'):
            try:
                await test_case.test_openai_query_processing()
                print("✅ Async OpenAI test passed")
            except Exception as e:
                print(f"❌ Async OpenAI test failed: {e}")
        
        if hasattr(test_case, 'test_full_computation_flow'):
            try:
                await test_case.test_full_computation_flow()
                print("✅ Async integration test passed")
            except Exception as e:
                print(f"❌ Async integration test failed: {e}")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "async-test":
    asyncio.run(run_async_tests())