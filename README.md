# Quantum Computation MCP Server 🚀🔬

A powerful Model Context Protocol (MCP) server that enables natural language quantum computation using OpenAI and IBM Quantum services.

## Features ✨

- **Natural Language Processing**: Convert English queries to quantum circuits using OpenAI GPT-4
- **IBM Quantum Integration**: Execute quantum circuits on real IBM quantum computers
- **Multiple Quantum Algorithms**: Support for Bell states, QFT, Grover's algorithm, and more
- **Real-time Results**: Get quantum computation results with detailed analysis
- **Backend Management**: List and select optimal quantum backends
- **Circuit Visualization**: ASCII art quantum circuit diagrams

## Supported Quantum Operations 🔬

- **Bell States**: Create maximally entangled quantum states
- **Quantum Fourier Transform (QFT)**: Apply discrete Fourier transform to quantum amplitudes  
- **Grover's Algorithm**: Quantum search with quadratic speedup
- **Quantum Random Number Generation**: True quantum randomness
- **Custom Circuits**: Define your own quantum operations
  (other algorithms will be added soon!)
  
## Installation 🛠️

### Prerequisites

1. **Python 3.8+**
2. **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com)
3. **IBM Quantum Account** - Sign up at [IBM Quantum Network](https://quantum-computing.ibm.com)

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/sakshiglaze/QuantumComputeMCPServer.git

# Install dependencies
pip install -r requirements.txt

```


## Quick Start 🚀

### 1. Start the MCP Server

```bash
python server.py
```

### 2. Connect from Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "quantum-computation": {
      "command": "python",
      "args": ["path/to/quantum_mcp_server.py"],
      "env": {}
    }
  }
}
```

### 3. Use in Claude

Ask Claude to use the quantum computation tools:

```
"Create a Bell state and run it on IBM Quantum using my API keys"
```

## API Keys Setup 🔑

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Keep it secure - never commit to version control

### IBM Quantum Token
1. Sign up at [IBM Quantum Network](https://quantum-computing.ibm.com)
2. Go to your [Account Settings](https://quantum-computing.ibm.com/account)
3. Copy your API token
4. Keep it secure - never commit to version control


## 🛠 Available Tools

The `quantum-mcp-server` exposes a set of powerful tools for quantum computation via the MCP (Multi-Modal Control Protocol) interface. These tools support natural language input, automatic circuit generation, and backend selection using Qiskit, IBM Quantum, and OpenAI.

---

### 🔹 `quantum_compute`

**Description:**  
Executes a quantum computation described in natural language.

**Input Schema:**
```json
{
  "query": "Create a Bell state using 2 qubits",
  "shots": 1024
}
```

**Features:**
- Parses natural language to identify quantum operations
- Supports Bell states, QFT, Grover's algorithm, teleportation, VQE, QAOA, and more
- Automatically selects between IBM Quantum hardware and local simulator
- Returns measurement results, circuit diagram, backend details, and analysis

---

### 🔹 `list_quantum_backends`

**Description:**  
Lists all available IBM Quantum backends (hardware + simulators).

**Input Schema:**
```json
{}
```

**Features:**
- Displays backend name, number of qubits, operational status, and type (simulator/real device)
- Useful for backend selection and monitoring availability

---

### 🔹 `quantum_circuit_info`

**Description:**  
Provides technical and educational information about supported quantum operations.

**Input Schema:**
```json
{
  "operation": "qft"
}
```

**Features:**
- Explains concepts like Bell state, QFT, Grover, Teleportation, VQE, QAOA, etc.
- Helpful for students, researchers, and developers working with quantum circuits

---

## Example Output 📊

```
🚀 Quantum Computation Results
================================

📝 Original Query: "Create a Bell state with maximum entanglement"

🔬 Operation: bell_state
🔢 Qubits Used: 2
💻 Backend: ibm_brisbane
🎯 Shots: 1024

📊 Measurement Results:
  |00⟩: 512 (50.0%)
  |11⟩: 512 (50.0%)

🔧 Circuit Properties:
  • Depth: 2
  • Width: 2

📈 Analysis:
  • Bell state created successfully
  • Shows quantum entanglement between qubits
  • Expect roughly equal probabilities for |00⟩ and |11⟩

🎨 Circuit Visualization:
     ┌───┐     ┌─┐   
q_0: ┤ H ├──■──┤M├───
     └───┘┌─┴─┐└╥┘┌─┐
q_1: ─────┤ X ├─╫─┤M├
          └───┘ ║ └╥┘
c: 2/═══════════╩══╩═
                0  1 

✅ Quantum computation completed successfully!
```

## Architecture 🏗️

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude/MCP    │    │  Quantum MCP    │    │  IBM Quantum    │
│     Client      │◄──►│     Server      │◄──►│    Backend      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │   (GPT-4)       │
                       └─────────────────┘
```

## Advanced Configuration ⚙️

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-key"
export IBM_QUANTUM_TOKEN="your-ibm-token"
export QUANTUM_BACKEND="ibm_brisbane"  # Optional: specify preferred backend
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

### Custom Circuit Parameters

The server accepts various parameters for different quantum operations:

```python
{
    "query": "Run Grover search for 2 marked items in 4-qubit space",
    "openai_key": "...",
    "ibm_token": "...",
    "shots": 2048,
    "custom_parameters": {
        "marked_items": [3, 7],
        "iterations": 2
    }
}
```

## Error Handling 🛡️

The server includes comprehensive error handling:

- **Invalid API Keys**: Clear error messages with setup instructions
- **Backend Unavailable**: Automatic fallback to simulators
- **Circuit Errors**: Validation and error correction
- **Network Issues**: Retry logic with exponential backoff

## Security Best Practices 🔒

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Rotate keys regularly**
4. **Monitor API usage** for unusual activity
5. **Use least-privilege access** when possible

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/sakshiglaze/QuantumComputeMCPServer.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest tests/
```

## Troubleshooting 🔧

### Common Issues

1. **"Services failed to initialize"**
   - Check API keys are valid and not expired
   - Verify network connectivity
   - Ensure IBM Quantum account is active

2. **"No backends available"**
   - IBM Quantum systems may be in maintenance
   - Try using simulator backends
   - Check your IBM Quantum access level

3. **"Circuit execution failed"**
   - Circuit may be too large for available backends
   - Try reducing the number of qubits
   - Use circuit optimization options

### Debug Mode

```bash
LOG_LEVEL=DEBUG python quantum_mcp_server.py
```

## Performance Tips 🚀

1. **Use simulators** for development and testing
2. **Optimize circuits** before real hardware execution  
3. **Batch multiple circuits** when possible
4. **Monitor queue times** on IBM backends
5. **Use appropriate shot counts** (1024 is usually sufficient)

## Roadmap 🗺️

- [ ] Support for more quantum algorithms (QAOA, VQE)
- [ ] Integration with other quantum cloud providers
- [ ] Quantum error correction support
- [ ] Circuit optimization recommendations
- [ ] Quantum machine learning algorithms
- [ ] Interactive circuit building
- [ ] Real-time collaboration features

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments 🙏

- [IBM Quantum](https://quantum-computing.ibm.com) for quantum computing infrastructure
- [OpenAI](https://openai.com) for natural language processing
- [Qiskit](https://qiskit.org) for quantum computing framework
- [Model Context Protocol](https://modelcontextprotocol.io) for the MCP specification
- [Anthropic](https://anthropic.com) for Claude and MCP tools

## Support 💬

- 📧 Email: sakshiglaze@gmail.com
- 💬 Discord: [Join our community](https://discord.gg/UD4jyGHP)
- 📖 Documentation: [Full Documentation](https://quantum-mcp-docs.example.com)

---
## Disclaimer

This project was originally developed using an earlier version of the IBM platform, which has since been deprecated. As the current platform requires credit card verification—which I do not possess—testing and further development have been temporarily halted.

Please note that the functionality of this application is significantly enhanced when used with the paid versions of IBM's server capabilities and similar services, such as OpenAI.

**Built with ❤️ for the quantum computing community**
