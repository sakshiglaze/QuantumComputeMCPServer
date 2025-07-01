#!/usr/bin/env python3
"""
Quantum Computation MCP Server - Fixed Version
Uses environment variables and has proper fallbacks
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass
from enum import Enum
import re

import openai
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Estimator
from qiskit.quantum_info import SparsePauliOp
from qiskit.visualization import circuit_drawer
from qiskit_aer import AerSimulator
from qiskit_aer import AerSimulator
import numpy as np

# MCP imports
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantumOperationType(Enum):
    """Types of quantum operations supported"""
    BELL_STATE = "bell_state"
    QUANTUM_FOURIER_TRANSFORM = "qft"
    GROVER_SEARCH = "grover"
    QUANTUM_TELEPORTATION = "teleportation"
    VARIATIONAL_QUANTUM_EIGENSOLVER = "vqe"
    QUANTUM_APPROXIMATE_OPTIMIZATION = "qaoa"
    CUSTOM_CIRCUIT = "custom"
    QUANTUM_RANDOM = "random"
    DEUTSCH_JOZSA = "deutsch_jozsa"
    BERNSTEIN_VAZIRANI = "bernstein_vazirani"

@dataclass
class QuantumComputationRequest:
    """Request structure for quantum computation"""
    query: str
    operation_type: QuantumOperationType
    parameters: Dict[str, Any]
    num_qubits: int = 2
    shots: int = 1024

# Create the server instance
server = Server("quantum-computation")

# Global variables for services
openai_client = None
ibm_service = None
simulator = None
simulator = None

def initialize_services():
    """Initialize services using environment variables"""
    global openai_client, ibm_service, simulator
    
    # Get API keys from environment
    openai_key = os.getenv('OPENAI_API_KEY')
    ibm_token = os.getenv('IBM_QUANTUM_TOKEN')
    
    logger.info(f"OpenAI key: {'Found' if openai_key else 'Missing'}")
    logger.info(f"IBM token: {'Found' if ibm_token else 'Missing'}")
    
    # Always initialize simulator as fallback
    try:
        simulator = AerSimulator()
        logger.info("Local simulator initialized")
    except Exception as e:
        logger.error(f"Failed to initialize simulator: {e}")
        return False
    
    # Try to initialize OpenAI (optional)
    if openai_key:
        try:
            openai_client = openai.OpenAI(api_key=openai_key)
            # Test it
            openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1
            )
            logger.info("OpenAI initialized successfully")
        except Exception as e:
            logger.warning(f"OpenAI initialization failed: {e}")
    
    # Try to initialize IBM Quantum (optional)
    if ibm_token:
        # Try different channels
        channels = ["ibm_quantum_platform", "ibm_cloud", "ibm_quantum"]
        
        for channel in channels:
            try:
                logger.info(f"Trying IBM channel: {channel}")
                QiskitRuntimeService.save_account(
                    channel=channel,
                    token=ibm_token,
                    overwrite=True
                )
                ibm_service = QiskitRuntimeService(channel=channel)
                
                # Test by listing backends
                backends = list(ibm_service.backends())
                logger.info(f"IBM Quantum initialized with {channel}: {len(backends)} backends")
                break
                
            except Exception as e:
                logger.warning(f"IBM channel {channel} failed: {e}")
                continue
    
    # Return True if at least simulator works
    return simulator is not None
def initialize_services():
    """Initialize services using environment variables"""
    global openai_client, ibm_service, simulator
    
    # Get API keys from environment
    openai_key = os.getenv('OPENAI_API_KEY')
    ibm_token = os.getenv('IBM_QUANTUM_TOKEN')
    
    logger.info(f"OpenAI key: {'Found' if openai_key else 'Missing'}")
    logger.info(f"IBM token: {'Found' if ibm_token else 'Missing'}")
    
    # Always initialize simulator as fallback
    try:
        simulator = AerSimulator()
        logger.info("Local simulator initialized")
    except Exception as e:
        logger.error(f"Failed to initialize simulator: {e}")
        return False
    
    # Try to initialize OpenAI (optional)
    if openai_key:
        try:
            openai_client = openai.OpenAI(api_key=openai_key)
            # Test it
            openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1
            )
            logger.info("OpenAI initialized successfully")
        except Exception as e:
            logger.warning(f"OpenAI initialization failed: {e}")
    
    # Try to initialize IBM Quantum (optional)
    if ibm_token:
        # Try different channels
        channels = ["ibm_quantum_platform", "ibm_cloud", "ibm_quantum"]
        
        for channel in channels:
            try:
                logger.info(f"Trying IBM channel: {channel}")
                QiskitRuntimeService.save_account(
                    channel=channel,
                    token=ibm_token,
                    overwrite=True
                )
                ibm_service = QiskitRuntimeService(channel=channel)
                
                # Test by listing backends
                backends = list(ibm_service.backends())
                logger.info(f"IBM Quantum initialized with {channel}: {len(backends)} backends")
                break
                
            except Exception as e:
                logger.warning(f"IBM channel {channel} failed: {e}")
                continue
    
    # Return True if at least simulator works
    return simulator is not None

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available quantum computation tools"""
    return [
        types.Tool(
            name="quantum_compute",
            description="Execute quantum computation with support for custom QFT input states",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language description of quantum computation to perform"
                    },
                    "shots": {
                        "type": "integer",
                        "description": "Number of shots for quantum execution (default: 1024)",
                        "default": 1024
                    }
                },
                "required": ["query"]
                "required": ["query"]
            }
        ),
        types.Tool(
            name="list_quantum_backends",
            description="List available IBM Quantum backends",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="quantum_circuit_info",
            description="Get information about quantum circuits and operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Type of quantum operation to get info about"
                    }
                },
                "required": ["operation"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    if arguments is None:
        arguments = {}
    
    try:
        if name == "quantum_compute":
            return await handle_quantum_compute(arguments)
        elif name == "list_quantum_backends":
            return await handle_list_backends(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_quantum_compute(arguments: Dict[str, Any]) -> list[types.TextContent]:
    """Handle quantum computation requests"""
    query = arguments.get("query", "")
    shots = arguments.get("shots", 1024)
    
    if not query:
        return [types.TextContent(type="text", text="Missing required parameter: query")]
    if not query:
        return [types.TextContent(type="text", text="Missing required parameter: query")]
    
    # Initialize services (uses environment variables)
    if not initialize_services():
        return [types.TextContent(type="text", text="Failed to initialize quantum services - check that qiskit-aer is installed")]
    # Initialize services (uses environment variables)
    if not initialize_services():
        return [types.TextContent(type="text", text="Failed to initialize quantum services - check that qiskit-aer is installed")]
    
    # Process query (with fallback if OpenAI not available)
    computation_request = await process_query_with_openai(query)
    
    # Create and execute circuit
    circuit = create_quantum_circuit(computation_request)
    
    # Execute (tries IBM, falls back to simulator)
    results = await execute_quantum(circuit, shots)
    
    # Format results
    response = format_results(computation_request, circuit, results)
    
    return [types.TextContent(type="text", text=response)]

async def handle_list_backends(arguments: Dict[str, Any]) -> list[types.TextContent]:
    """List available IBM Quantum backends"""
    if not initialize_services():
        return [types.TextContent(type="text", text="Failed to initialize services")]
    
    if ibm_service:
        try:
            backends = list(ibm_service.backends())
            
            response = f"IBM Quantum Backends ({len(backends)} found):\n\n"
            for backend in backends:
                status = backend.status()
                operational = "✅ Up" if status.operational else "❌ Down"
                
                response += f"• **{backend.name}**\n"
                response += f"  - Qubits: {backend.num_qubits}\n"
                response += f"  - Status: {operational}\n"
                response += f"  - Simulator: {'Yes' if backend.configuration().simulator else 'No'}\n\n"
            
            return [types.TextContent(type="text", text=response)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error listing backends: {e}")]
    else:
        return [types.TextContent(type="text", text="IBM Quantum not available. Using local simulator only.\n\nTo enable IBM Quantum:\n1. Set IBM_QUANTUM_TOKEN in environment\n2. Get token from: https://quantum.ibm.com/account")]

async def handle_circuit_info(arguments: Dict[str, Any]) -> list[types.TextContent]:
    """Provide information about quantum circuits and operations"""
    operation = arguments.get("operation", "").lower()
    
    if not operation:
        return [types.TextContent(type="text", text="Missing required parameter: operation")]
    
    info_dict = {
        "bell_state": "Bell states are maximally entangled quantum states of two qubits. They demonstrate quantum superposition and entanglement.",
        "qft": "Quantum Fourier Transform is a quantum algorithm that applies the discrete Fourier transform to quantum amplitudes.",
        "grover": "Grover's algorithm provides quadratic speedup for searching unsorted databases using quantum amplitude amplification.",
        "teleportation": "Quantum teleportation transfers quantum information from one location to another using entanglement and classical communication.",
        "vqe": "Variational Quantum Eigensolver finds the ground state energy of molecules using a hybrid quantum-classical approach.",
        "qaoa": "Quantum Approximate Optimization Algorithm solves combinatorial optimization problems on near-term quantum devices."
    }
    
    info = info_dict.get(operation, f"Information about '{operation}' is not available. Available operations: {list(info_dict.keys())}")
    
    return [types.TextContent(type="text", text=info)]

async def process_query_with_openai(query: str) -> QuantumComputationRequest:
    """Process natural language query using OpenAI to determine quantum operation"""
    global openai_client
    
    if openai_client:
        try:
            prompt = f"""
            Analyze this quantum computation request and extract the key information:
            Query: "{query}"
            
            Determine:
            1. What type of quantum operation is being requested?
            2. How many qubits are needed?
            3. What parameters are specified?
            
            Available operations:
            - bell_state: Create Bell states (entangled pairs)
            - qft: Quantum Fourier Transform
            - grover: Grover's search algorithm
            - teleportation: Quantum teleportation
            - vqe: Variational Quantum Eigensolver
            - qaoa: Quantum Approximate Optimization Algorithm
            - custom: Custom quantum circuit
            - random: Quantum random number generation
            - deutsch_jozsa: Deutsch-Jozsa algorithm
            - bernstein_vazirani: Bernstein-Vazirani algorithm
            
            Respond in JSON format:
            {{
                "operation_type": "operation_name",
                "num_qubits": number,
                "parameters": {{}},
                "reasoning": "explanation"
            }}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return QuantumComputationRequest(
                query=query,
                operation_type=QuantumOperationType(result["operation_type"]),
                parameters=result["parameters"],
                num_qubits=result["num_qubits"]
            )
        except Exception as e:
            logger.warning(f"OpenAI processing failed: {e}, using local processing")
    
    # Fallback to local processing
    return process_query_locally(query)

def process_query_locally(query: str) -> QuantumComputationRequest:
    """Process query using simple pattern matching (fallback when OpenAI fails)"""
    query_lower = query.lower()
    
    # Pattern matching for different operations
    if any(word in query_lower for word in ['bell', 'entangl', 'epr']):
        return QuantumComputationRequest(
            query=query,
            operation_type=QuantumOperationType.BELL_STATE,
            parameters={},
            num_qubits=2
        )
    
    elif any(word in query_lower for word in ['random', 'rng', 'number']):
        num_qubits = 3  # default
        numbers = re.findall(r'\d+', query)
        if numbers:
            num_qubits = min(int(numbers[0]), 5)
        return QuantumComputationRequest(
            query=query,
            operation_type=QuantumOperationType.QUANTUM_RANDOM,
            parameters={},
            num_qubits=num_qubits
        )
    
    else:
        # Default
        return QuantumComputationRequest(
            query=query,
            operation_type=QuantumOperationType.BELL_STATE,
            parameters={},
            num_qubits=2
        )

def extract_input_state_from_query(query: str) -> str:
    """Extract quantum state specification from the query"""
    
    # Look for patterns like |psi> = (1/sqrt(2))(|00> + |10>)
    # or |ψ⟩ = (1/√2)(|0⟩ + |2⟩)
    
    if '|00⟩ + |10⟩' in query or '|00> + |10>' in query:
        return "superposition_0_2"  # |00⟩ + |10⟩
    elif '|0⟩ + |2⟩' in query or '|0> + |2>' in query:
        return "superposition_0_2"  # Same as above in decimal notation
    elif '|01⟩ + |11⟩' in query or '|01> + |11>' in query:
        return "superposition_1_3"  # |01⟩ + |11⟩
    elif '|0⟩ + |1⟩' in query or '|0> + |1>' in query:
        return "superposition_0_1"  # |0⟩ + |1⟩
    elif 'equal superposition' in query.lower():
        return "equal_superposition"  # All computational basis states
    else:
        # Default to the user's specific case
        return "superposition_0_2"  # |00⟩ + |10⟩

def create_quantum_circuit(request: QuantumComputationRequest) -> QuantumCircuit:
    """Create quantum circuit with proper input state preparation + operation"""
    
    if request.operation_type == QuantumOperationType.QUANTUM_FOURIER_TRANSFORM:
        return create_qft_circuit_with_input_state(request)
    
    elif request.operation_type == QuantumOperationType.BELL_STATE:
        circuit = QuantumCircuit(2, 2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()
        return circuit
    
    elif request.operation_type == QuantumOperationType.QUANTUM_RANDOM:
        circuit = QuantumCircuit(request.num_qubits, request.num_qubits)
        for i in range(request.num_qubits):
            circuit.h(i)
    
    else:
        # Default to superposition_0_2
        circuit.h(0)
    
    # Add a barrier to separate state preparation from QFT
    circuit.barrier()
    
    # Step 2: Apply 2-qubit Quantum Fourier Transform
    apply_2qubit_qft(circuit)
    
    # Step 3: Add measurements
    circuit.measure_all()
    
    return circuit

async def execute_quantum(circuit: QuantumCircuit, shots: int = 1024):
    """Execute quantum circuit (tries IBM, falls back to simulator)"""
    global ibm_service, simulator
    
    # Try IBM Quantum first if available
    if ibm_service:
        try:
            logger.info("Attempting IBM Quantum execution...")
            
            # Get the least busy real backend (not simulator)
            backends = [b for b in ibm_service.backends() 
                       if b.status().operational and not b.configuration().simulator]
            
            if backends:
                # Sort by queue length
                backends.sort(key=lambda b: b.status().pending_jobs)
                backend = backends[0]
                
                logger.info(f"Using IBM backend: {backend.name}")
                
                # Transpile and execute
                transpiled_circuit = transpile(circuit, backend, optimization_level=1)
                sampler = Sampler(backend)
                job = sampler.run([transpiled_circuit], shots=shots)
                result = job.result()
                
                return {
                    "backend": backend.name,
                    "backend_type": "🌟 IBM Quantum Hardware",
                    "shots": shots,
                    "counts": result[0].data.meas.get_counts(),
                    "circuit_depth": transpiled_circuit.depth(),
                    "circuit_width": transpiled_circuit.width()
                }
            else:
                logger.info("No operational IBM hardware backends available")
                
        except Exception as e:
            logger.warning(f"IBM Quantum execution failed: {e}")
    
    # Fallback to local simulator
    logger.info("Using local simulator...")
    job = simulator.run(circuit, shots=shots)
    result = job.result()
    
    return {
        "backend": "aer_simulator",
        "backend_type": "🖥️  Local Simulator",
        "shots": shots,
        "counts": result.get_counts(),
        "circuit_depth": circuit.depth(),
        "circuit_width": circuit.width()
    }

def format_results(request: QuantumComputationRequest, circuit: QuantumCircuit, results: Dict) -> str:
    """Format the quantum computation results with QFT analysis"""
    
    if request.operation_type == QuantumOperationType.QUANTUM_FOURIER_TRANSFORM:
        return format_qft_results(request, circuit, results)
    else:
        return format_general_results(request, circuit, results)

def format_qft_results(request: QuantumComputationRequest, circuit: QuantumCircuit, results: Dict) -> str:
    """Format QFT-specific results with frequency analysis"""
    
    input_state = request.parameters.get('input_state', 'superposition_0_2')
    
    response = f"""
🚀 Quantum Fourier Transform Results
=====================================

📝 Original Query: "{request.query}"

🔬 Operation: 2-Qubit Quantum Fourier Transform (QFT)
📊 Input State: {get_input_state_description(input_state)}
💻 Backend: {results['backend']} ({results['backend_type']})
🎯 Shots: {results['shots']}

📊 QFT Output Measurements:
"""
    
    # Add measurement counts
    counts = results['counts']
    total_shots = sum(counts.values())
    
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        probability = count / total_shots
        percentage = probability * 100
        response += f"  |{state}⟩: {count:4d} ({percentage:5.1f}%)\n"
    
    response += f"""
🔧 Circuit Properties:
  • Total Depth: {results['circuit_depth']}
  • Width: {results['circuit_width']}
  • QFT Depth: ~3 (theoretical)

🧮 Frequency Analysis:
{analyze_qft_frequencies(input_state, counts)}

🎨 QFT Circuit Structure:
{circuit.draw(output='text')}

✅ Quantum Fourier Transform completed successfully!
"""
    
    return response

def get_input_state_description(input_state: str) -> str:
    """Get human-readable description of input state"""
    descriptions = {
        "superposition_0_2": "|ψ⟩ = (1/√2)(|00⟩ + |10⟩) - States 0 and 2",
        "superposition_1_3": "|ψ⟩ = (1/√2)(|01⟩ + |11⟩) - States 1 and 3", 
        "superposition_0_1": "|ψ⟩ = (1/√2)(|0⟩ + |1⟩) - Single qubit superposition",
        "equal_superposition": "|ψ⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) - All states"
    }
    return descriptions.get(input_state, "Custom superposition state")

def analyze_qft_frequencies(input_state: str, counts: Dict[str, int]) -> str:
    """Analyze the frequency components revealed by QFT"""
    
    if input_state == "superposition_0_2":
        return """
🎯 **Expected QFT Result for |ψ⟩ = (1/√2)(|00⟩ + |10⟩)**:

📊 **Theoretical Prediction**:
  • |00⟩: 50% (k=0, DC component)
  • |01⟩: 0%  (k=1, forbidden by symmetry)
  • |10⟩: 50% (k=2, Nyquist frequency)  
  • |11⟩: 0%  (k=3, forbidden by symmetry)

🔍 **Frequency Interpretation**:
  • **k=0 (|00⟩)**: DC/constant component
  • **k=2 (|10⟩)**: Maximum frequency (period-2 oscillation)
  • **k=1,3**: Absent due to even-parity symmetry
  
⚡ **Key Insight**: This state has perfect frequency filtering!
   Only DC and Nyquist frequency components are present.
   
🌟 **Remarkable Property**: QFT(|ψ⟩) = |ψ⟩ 
   This input state is an eigenstate of the QFT operator!
"""
    
    elif input_state == "superposition_1_3":
        return """
🎯 **Expected QFT Result for |ψ⟩ = (1/√2)(|01⟩ + |11⟩)**:

📊 **Theoretical Prediction**:
  • |00⟩: 0%  (k=0, forbidden)
  • |01⟩: 50% (k=1, fundamental frequency)
  • |10⟩: 0%  (k=2, forbidden)
  • |11⟩: 50% (k=3, high frequency)

🔍 **Frequency Interpretation**:
  • Shows odd-parity frequency components only
  • Complementary to the even-parity case
"""
    
    elif input_state == "equal_superposition":
        return """
🎯 **Expected QFT Result for Equal Superposition**:

📊 **Theoretical Prediction**:
  • |00⟩: 100% (only k=0 survives)
  • All other states: 0%

🔍 **Frequency Interpretation**:
  • Pure DC component only
  • All frequency information washed out by averaging
"""
    
    else:
        return "Custom state frequency analysis not available."

def format_general_results(request: QuantumComputationRequest, circuit: QuantumCircuit, results: Dict) -> str:
    """Format results for non-QFT operations"""
    
    response = f"""
🚀 Quantum Computation Results
================================

📝 Original Query: "{request.query}"

🔬 Operation: {request.operation_type.value}
🔢 Qubits Used: {request.num_qubits}
💻 Backend: {results['backend']} ({results['backend_type']})
💻 Backend: {results['backend']} ({results['backend_type']})
🎯 Shots: {results['shots']}

📊 Measurement Results:
"""
    
    # Add measurement counts
    counts = results['counts']
    total_shots = sum(counts.values())
    
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        probability = count / total_shots
        percentage = probability * 100
        response += f"  |{state}⟩: {count} ({percentage:.1f}%)\n"
    
    response += f"""
🔧 Circuit Properties:
  • Depth: {results['circuit_depth']}
  • Width: {results['circuit_width']}

📈 Analysis:
"""
    
    # Add operation-specific analysis
    if request.operation_type == QuantumOperationType.BELL_STATE:
        response += "  • Bell state created successfully\n"
        response += "  • Shows quantum entanglement between qubits\n"
        response += "  • Expect roughly equal probabilities for |00⟩ and |11⟩\n"
    
    elif request.operation_type == QuantumOperationType.QUANTUM_RANDOM:
        if total_shots > 0:
            entropy = -sum((count/total_shots) * np.log2(count/total_shots) for count in counts.values() if count > 0)
            response += f"  • Quantum randomness generated\n"
            response += f"  • Entropy: {entropy:.3f} bits\n"
            response += f"  • Maximum possible entropy: {request.num_qubits} bits\n"
    
    elif request.operation_type == QuantumOperationType.GROVER_SEARCH:
        response += "  • Grover's algorithm executed\n"
        response += "  • Amplifies probability of marked states\n"
        response += "  • Look for states with higher probabilities\n"
    
    # Add special note for IBM hardware
    if "🌟 IBM Quantum Hardware" in results['backend_type']:
        response += "\n⭐ **SPECIAL**: These results came from real quantum hardware!\n"
        response += "   • Each measurement is a genuine quantum event\n"
        response += "   • Results may show quantum noise and decoherence\n"
    
    try:
        circuit_str = circuit.draw(output='text')
        response += f"""
🎨 Circuit Visualization:
{circuit.draw(output='text')}

✅ Quantum computation completed successfully!
"""
    
    return response

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="quantum-computation",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())