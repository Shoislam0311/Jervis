# JarvisClone AI Assistant

🤖 **JarvisClone** is a fully functional, cross-platform AI assistant application with conversational chat, web search integration, multilingual support, and voice capabilities.

## ✨ Features

- **Conversational AI**: Natural language chat with contextual memory using OpenRouter.ai's Gemma model
- **Web Search Integration**: Real-time information retrieval via DuckDuckGo API
- **Multilingual Support**: Bengali, English, and Hindi language capabilities
- **Voice Synthesis**: Text-to-speech using puter.ai service
- **Multiple Interfaces**: Command-line interface and web dashboard
- **Plugin Architecture**: Extensible design for adding new features
- **Containerized Deployment**: Docker support for easy deployment
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- Docker (optional, for containerized deployment)
- OpenRouter.ai API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/JarvisClone.git
   cd JarvisClone
   ```

2. **Set up environment variables**
   ```bash
   export OPENROUTER_API_KEY="your_api_key_here"
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the CLI interface**
   ```bash
   python -m assistant.core
   ```

5. **Run the web dashboard**
   ```bash
   cd app/web_ui
   source venv/bin/activate
   python src/main.py
   ```
   
   Open http://localhost:5000 in your browser.

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Web Dashboard: http://localhost:5000
   - API Endpoints: http://localhost:5000/api/

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   User CLI      │    │  Web Dashboard  │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
            ┌────────▼────────┐
            │  JarvisCore     │
            │  (AI Assistant) │
            └─────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼───┐   ┌───▼───┐   ┌────▼───┐
   │Memory  │   │Search │   │  TTS   │
   │Store   │   │ API   │   │Service │
   └────────┘   └───────┘   └────────┘
```

## 📖 Usage Examples

### Command Line Interface

```bash
# Start the CLI
python -m assistant.core

# Example conversation
You: Hello, how are you?
Jarvis: Hello! I'm doing well, thank you for asking. How can I assist you today?

You: search for latest Python news
Jarvis: Based on the latest search results, here are some recent Python developments...

You: speak Thank you for the information
Jarvis: Thank you for the information
[Audio plays through speakers]
```

### Web Dashboard

The web dashboard provides a modern, responsive interface with:
- Real-time chat interface
- Language selection (English, Bengali, Hindi)
- Voice response capabilities
- Message history
- Mobile-friendly design

### API Endpoints

**Chat API**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how can you help me?"}'
```

**Text-to-Speech API**
```bash
curl -X POST http://localhost:5000/api/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test message"}'
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENROUTER_API_KEY` | OpenRouter.ai API key | None | Yes |
| `FLASK_ENV` | Flask environment | `development` | No |
| `MEMORY_FILE` | Path to memory storage file | `memory.json` | No |

### Memory Storage

JarvisClone uses a local JSON-based memory store by default. For production deployments, consider upgrading to:
- PostgreSQL for relational data
- Redis for caching
- ChromaDB for vector storage

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=assistant --cov-report=html
```

### Test Coverage

The test suite includes:
- Unit tests for core functionality
- Integration tests for API endpoints
- Mock tests for external services
- Performance tests for memory management

## 🚀 Deployment

### Docker Deployment

1. **Production deployment**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

2. **Environment configuration**
   ```bash
   # Create .env file
   echo "OPENROUTER_API_KEY=your_key_here" > .env
   ```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jarvisclone
spec:
  replicas: 3
  selector:
    matchLabels:
      app: jarvisclone
  template:
    spec:
      containers:
      - name: jarvisclone
        image: jarvisclone/ai-assistant:latest
        ports:
        - containerPort: 5000
```

### VPS Deployment

1. **Server setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   sudo apt install docker-compose -y
   ```

2. **Application deployment**
   ```bash
   git clone https://github.com/your-username/JarvisClone.git
   cd JarvisClone
   docker-compose up -d
   ```

## 🔌 Plugin Development

JarvisClone supports a plugin architecture for extending functionality:

```python
# Example plugin structure
class CalendarPlugin:
    def __init__(self, jarvis_core):
        self.core = jarvis_core
    
    def handle_request(self, user_input):
        if "calendar" in user_input.lower():
            return self.get_calendar_events()
    
    def get_calendar_events(self):
        # Implementation here
        return "Your calendar events..."

# Register plugin
jarvis.register_plugin(CalendarPlugin(jarvis))
```

## 🌍 Multilingual Support

JarvisClone supports multiple languages:

- **English**: Default language with full feature support
- **Bengali (বাংলা)**: Native support for Bengali conversations
- **Hindi (हिंदी)**: Hindi language interface and responses

Language switching is automatic based on user input or can be manually selected in the web dashboard.

## 🔒 Security

### Security Features

- API key protection through environment variables
- CORS configuration for web security
- Input validation and sanitization
- Rate limiting for API endpoints
- Secure session management

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use HTTPS** in production deployments
3. **Implement rate limiting** for public APIs
4. **Regular security updates** for dependencies
5. **Monitor logs** for suspicious activity

## 📊 Monitoring and Logging

### Application Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

The application includes health check endpoints:

```bash
# Check application health
curl http://localhost:5000/health

# Check API status
curl http://localhost:5000/api/status
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   pytest tests/
   ```
5. **Submit a pull request**

### Code Style

- Follow PEP 8 Python style guidelines
- Use black for code formatting
- Add type hints where appropriate
- Write comprehensive docstrings
- Include unit tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenRouter.ai](https://openrouter.ai/) for LLM API access
- [DuckDuckGo](https://duckduckgo.com/) for search API
- [puter.ai](https://puter.ai/) for text-to-speech services
- The open-source community for inspiration and tools

## 📞 Support

- **Documentation**: [Wiki](https://github.com/your-username/JarvisClone/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/JarvisClone/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/JarvisClone/discussions)
- **Email**: support@jarvisclone.com

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Core conversational AI
- ✅ Web search integration
- ✅ Basic TTS support
- ✅ Web dashboard
- ✅ Docker deployment

### Version 1.1 (Planned)
- 🔄 Plugin system enhancement
- 🔄 Advanced memory management
- 🔄 Mobile app development
- 🔄 Voice input support
- 🔄 Calendar integration

### Version 2.0 (Future)
- 📋 Advanced AI capabilities
- 📋 Multi-user support
- 📋 Cloud deployment options
- 📋 Enterprise features
- 📋 API marketplace

---

**Made with ❤️ by the JarvisClone Team**

