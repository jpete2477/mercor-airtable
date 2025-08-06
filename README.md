# Applicant Tracking System

A modern, containerized applicant tracking system built with Flask, Airtable, and LLM integration. Features automatic JSON compression, intelligent candidate evaluation, and configurable shortlisting rules.

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
git clone <repository-url>
cd Mercor-Airtable
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

Create an Airtable base with these tables:

#### Applicants
- `Applicant ID` (AutoNumber)
- `Compressed JSON` (Long Text) 
- `LLM Summary` (Long Text)
- `LLM Score` (Number)
- `Status` (Single Select: Pending, Processed, Error)
- `Last Hash` (Long Text)

#### Personal Details  
- `Full Name` (Single Line Text, required)
- `Email` (Email)
- `Location` (Single Line Text)
- `LinkedIn` (URL)
- `Applicant ID` (Link to Applicants)

#### Work Experience
- `Company` (Single Line Text)
- `Title` (Single Line Text)  
- `Start` (Date)
- `End` (Date)
- `Technologies` (Multiple Select)
- `Applicant ID` (Link to Applicants)

#### Salary Preferences
- `Preferred Rate` (Number)
- `Min Rate` (Number)
- `Currency` (Single Select: USD, EUR, GBP, etc.)
- `Availability` (Number)
- `Applicant ID` (Link to Applicants)

#### Shortlisted Leads
- `Applicant` (Link to Applicants)
- `Compressed JSON` (Long Text)
- `Score` (Number)
- `Score Reason` (Long Text) 
- `Created At` (Date/Time)

#### Shortlist Rules
- `Criterion` (Single Line Text)
- `Rule` (Single Line Text)
- `Points` (Number)
- `Active` (Checkbox)
- `Description` (Long Text)

### 4. Add Sample Shortlist Rules

Add these records to your Shortlist Rules table:

| Criterion | Rule | Points | Active | Description |
|-----------|------|---------|--------|-------------|
| experience | >=3 years | 1 | ✓ | At least 3 years experience |
| compensation | <=$100/hr | 1 | ✓ | Rate under $100/hour |
| location | US only | 1 | ✓ | Located in United States |
| availability | >=35 hours | 1 | ✓ | Full-time availability |

### 5. Launch Application

```bash
# Production mode
docker-compose up -d

# Development mode (with logs)
docker-compose up
```

### 6. Access Application

- **Application Form**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/admin  
- **Health Check**: http://localhost:5000/api/health

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up test-runner

# Run tests in development
docker-compose -f docker-compose.test.yml up app-test

# Run specific test file
docker-compose -f docker-compose.test.yml run app-test python -m pytest tests/test_compression.py -v
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
│   ├── main.py                 # Flask application
│   ├── models/
│   │   ├── airtable_client.py  # Airtable integration
│   │   ├── compression.py      # JSON compression
│   │   ├── llm_service.py      # LLM integration  
│   │   └── shortlist_engine.py # Shortlisting logic
│   ├── templates/              # HTML templates
│   │   ├── base.html
│   │   ├── index.html          # Application form
│   │   └── admin.html          # Admin dashboard
│   └── static/                 # Static assets
├── config/
│   └── settings.py             # Configuration
├── tests/                      # Test suite
├── docker-compose.yml          # Production compose
├── docker-compose.test.yml     # Test compose
├── Dockerfile                  # Container definition
└── requirements.txt            # Python dependencies
```

## 🚀 Production Deployment

### With SSL/HTTPS

1. Create SSL certificates in `./ssl/` directory
2. Update `nginx.conf` with your domain
3. Deploy with nginx:

```bash
docker-compose --profile production up -d
```

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