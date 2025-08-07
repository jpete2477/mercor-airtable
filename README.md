# Airtable-based Applicant Tracking System

A modern, containerized applicant tracking system built with Flask, Airtable, and AI integration. Features automatic JSON compression, intelligent candidate evaluation, and a responsive admin dashboard.

## 🔗 Repository
**GitHub**: https://github.com/jpete2477/mercor-airtable

📋 **Full Documentation**: See [PROJECT-DOC.md](PROJECT-DOC.md) for comprehensive technical documentation.

## ✨ Key Highlights

- **🎯 Production Ready**: Fully containerized with Docker, includes health checks and error handling
- **🤖 AI-Powered**: Integrates OpenAI/Anthropic for intelligent candidate evaluation
- **📊 Real-time Dashboard**: Beautiful admin interface with live statistics and candidate management
- **🗜️ Smart Compression**: Advanced JSON compression with hash-based change detection
- **⚡ High Performance**: Redis caching, rate limiting, and optimized database queries
- **🔧 Developer Friendly**: Hot reloading, comprehensive tests, detailed documentation

## 🎥 Quick Demo

1. **Application Form**: Candidates submit applications through a clean, responsive form
2. **Automatic Processing**: Data is compressed, stored in Airtable, and evaluated by AI
3. **Admin Dashboard**: Real-time view of all candidates with scores, statistics, and management tools
4. **API Integration**: Full REST API for programmatic access and integrations

## 🚀 Features

- **Modern Web Interface**: Clean, responsive forms and admin dashboard
- **Airtable Integration**: Seamless data storage with structured relationships  
- **JSON Compression**: Efficient data compression with hash-based deduplication
- **LLM Evaluation**: AI-powered candidate assessment using OpenAI or Anthropic
- **Smart Shortlisting**: Configurable rules-based candidate filtering
- **Docker Ready**: Fully containerized with Docker Compose orchestration
- **Rate Limiting**: Redis-based API protection
- **Comprehensive Testing**: Unit tests with pytest

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Web Frontend  │────│ Flask API    │────│   Airtable      │
│   (HTML/JS)     │    │ (Python)     │    │   Database      │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                       ┌──────┴──────┐
                       │             │
                ┌──────▼──────┐ ┌────▼─────┐
                │    Redis    │ │   LLM    │
                │   Cache     │ │  Service │
                └─────────────┘ └──────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- Airtable account with API key
- OpenAI or Anthropic API key
- Git

## ⚡ Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/jpete2477/mercor-airtable.git
cd mercor-airtable
cp .env.example .env
```

### 2. Set Up Environment Variables

Edit `.env` file with your credentials:

```bash
# Required
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional
SECRET_KEY=your-secure-secret-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

### 3. Set Up Airtable Schema

Create an Airtable base with these tables (see [AIRTABLE_SETUP.md](AIRTABLE_SETUP.md) for detailed setup):

#### Applicants *(Required)*
- `Name` (Single line text) - Primary field
- `Status` (Single select: Pending, Processed)
- `Compressed JSON` (Long text) - Stores compressed applicant data
- `Last Hash` (Single line text) - For change detection
- `LLM Summary` (Long text) - AI evaluation summary
- `LLM Score` (Number) - AI-generated score

#### Personal Details *(Required)*
- `Applicant Record` (Link to Applicants)
- `Full Name` (Single line text)
- `Email Address` (Email) 
- `City Location` (Single line text)
- `LinkedIn Profile` (URL)

#### Additional Tables *(Optional - for full functionality)*
- **Work Experience** - Job history details
- **Salary Preferences** - Compensation requirements  
- **Shortlist Rules** - Configurable scoring criteria
- **Shortlisted Leads** - Qualified candidates

> **Note**: The current implementation works with just the Applicants and Personal Details tables. Additional tables can be added later for enhanced functionality.

### 4. Launch Application

```bash
# Production mode
docker-compose up -d

# Development mode (with logs)
docker-compose up
```

### 5. Access Application

- **Application Form**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/admin  
- **Health Check**: http://localhost:5000/api/health

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
docker-compose exec app python -m pytest

# Run tests with coverage
docker-compose exec app python -m pytest --cov=app

# Run specific test file
docker-compose exec app python -m pytest tests/test_compression.py -v
```

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Application form |
| GET | `/admin` | Admin dashboard |
| POST | `/api/submit-application` | Submit new application |
| POST | `/api/process-applicant/<id>` | Process applicant data |
| GET | `/api/shortlisted-leads` | Get shortlisted candidates |
| GET | `/api/applicant/<id>` | Get applicant details |
| POST | `/api/decompress-applicant/<id>` | Restore applicant data |
| GET | `/api/health` | Health check |

### Example API Usage

Submit application:
```bash
curl -X POST http://localhost:5000/api/submit-application \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com", 
    "location": "San Francisco, CA",
    "preferred_rate": 85,
    "work_experience": [{
      "company": "Tech Corp",
      "title": "Software Engineer",
      "start": "2020-01",
      "end": "2023-12",
      "technologies": ["Python", "React"]
    }]
  }'
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AIRTABLE_API_KEY` | Required | Airtable API key |
| `AIRTABLE_BASE_ID` | Required | Airtable base ID |
| `OPENAI_API_KEY` | Optional | OpenAI API key |
| `ANTHROPIC_API_KEY` | Optional | Anthropic API key |
| `LLM_PROVIDER` | `openai` | LLM provider (`openai` or `anthropic`) |
| `LLM_MODEL` | `gpt-4o-mini` | LLM model to use |
| `LLM_MAX_TOKENS` | `512` | Max tokens per LLM call |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `MAX_JSON_SIZE` | `102400` | Max compressed JSON size (bytes) |
| `SHORTLIST_MIN_SCORE` | `2` | Minimum score for shortlisting |
| `RATE_LIMIT_PER_MINUTE` | `60` | API rate limit |

### Shortlisting Rules

Rules are configured in Airtable. Supported rule types:

- **Experience**: `>=4 years`, `>=2 years in Python`
- **Compensation**: `<=$100/hr`, `>=50/hr`  
- **Location**: `US only`, `Europe`, `remote`
- **Technology**: `has Python`, `React experience`
- **Availability**: `>=40 hours`, `full-time`

## 🔧 Development

### Local Development Setup

```bash
# Install dependencies locally
pip install -r requirements.txt

# Set environment variables
export FLASK_DEBUG=true
export AIRTABLE_API_KEY=your_key
export AIRTABLE_BASE_ID=your_base_id

# Run development server
python app/main.py
```

### Project Structure

```
mercor-airtable/
├── app/
│   ├── main.py                 # Flask application entry point
│   ├── models/                 # Business logic components
│   │   ├── airtable_client.py  # Airtable API integration
│   │   ├── compression.py      # JSON compression utilities
│   │   ├── llm_service.py      # AI evaluation service  
│   │   └── shortlist_engine.py # Candidate ranking logic
│   └── templates/              # Jinja2 HTML templates
│       ├── base.html           # Base template with navbar
│       ├── index.html          # Application form
│       └── admin.html          # Admin dashboard
├── config/
│   └── settings.py             # Environment configuration
├── tests/                      # Test suite with pytest
│   ├── test_compression.py     # Compression tests
│   └── test_shortlist_engine.py # Shortlisting tests
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Application container
├── requirements.txt            # Python dependencies
├── PROJECT-DOC.md              # Comprehensive documentation
└── AIRTABLE_SETUP.md          # Database setup guide
```

## 🚀 Production Deployment

### Environment Considerations

- Use strong `SECRET_KEY` in production
- Set `FLASK_DEBUG=false`
- Configure proper Redis persistence
- Set up log aggregation
- Monitor API usage and costs
- Regular Airtable backups

## 🔍 Monitoring & Maintenance

### Health Checks

The application includes built-in health checks:
- Container health via Docker
- Airtable connectivity
- Redis status
- LLM provider status

### Log Monitoring

View application logs:
```bash
docker-compose logs -f app
```

### Performance Tuning

- Adjust Redis memory limits
- Scale with multiple app containers
- Monitor LLM token usage
- Optimize Airtable query patterns

## 🛠️ Troubleshooting

### Common Issues

**Airtable Connection Failed**
- Verify API key and base ID
- Check table names match exactly
- Ensure proper field types in Airtable

**LLM Evaluation Errors**
- Verify API key for chosen provider
- Check token limits and quotas
- Review model availability

**Rate Limiting Issues** 
- Adjust `RATE_LIMIT_PER_MINUTE`
- Scale Redis if needed
- Check client request patterns

**Docker Issues**
- Ensure Docker daemon is running
- Check port conflicts (5000, 6379)
- Verify environment file exists

### Debug Mode

Enable debug logging:
```bash
export FLASK_DEBUG=true
docker-compose up
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`docker-compose -f docker-compose.test.yml up test-runner`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Airtable API Documentation](https://airtable.com/developers/web/api/introduction)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Docker Documentation](https://docs.docker.com)

---

**Built with ❤️ using Flask, Airtable, and modern DevOps practices**