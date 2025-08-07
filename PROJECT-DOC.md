# Airtable-based Applicant Tracking System

## Overview

This is a comprehensive applicant tracking system built with Flask, Airtable, and AI integration. The system automates the entire candidate evaluation process from application submission to shortlisting, featuring JSON compression, LLM-powered candidate evaluation, and a responsive admin dashboard.

## Github Repo
https://github.com/jpete2477/mercor-airtable

## Features

### Core Functionality
- **Web-based Application Forms**: Responsive forms for candidate submission
- **Airtable Integration**: Seamless data storage and retrieval from Airtable base
- **JSON Compression**: Efficient data compression with hash-based deduplication
- **AI-Powered Evaluation**: LLM integration for intelligent candidate assessment
- **Automated Shortlisting**: Rule-based scoring system for candidate ranking
- **Admin Dashboard**: Real-time statistics and candidate management interface
- **RESTful API**: Complete API endpoints for all operations

### Technical Features
- **Docker Containerization**: Easy deployment with Docker and Docker Compose
- **Hot Reloading**: Development-friendly hot reloading support
- **Rate Limiting**: Built-in API rate limiting with Redis support
- **Error Handling**: Comprehensive error handling and logging
- **Responsive Design**: Bootstrap-based mobile-friendly interface
- **Caching**: Redis-based caching for improved performance

## Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Flask API      │    │   Airtable DB   │
│   (Bootstrap)   │◄──►│   (Python)       │◄──►│   (Cloud)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   AI Services    │
                       │ (OpenAI/Anthropic)│
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Redis Cache    │
                       │   (Optional)     │
                       └──────────────────┘
```

### Data Flow

1. **Application Submission**: Candidates fill out web form
2. **Data Storage**: Information stored in Airtable with proper relationships
3. **Compression**: JSON data compressed with hash-based deduplication
4. **AI Evaluation**: LLM processes candidate data for insights and scoring
5. **Shortlisting**: Rule-based engine evaluates against configurable criteria
6. **Admin Dashboard**: Real-time view of candidates and statistics

## Installation & Setup

### Prerequisites

- Docker and Docker Compose
- Airtable account and API key
- OpenAI or Anthropic API key (optional, for AI features)
- Git

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jpete2477/mercor-airtable.git
   cd mercor-airtable
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

3. **Configure Airtable**:
   - Create Airtable base using the schema in `AIRTABLE_SETUP.md`
   - Add your `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID` to `.env`

4. **Start the application**:
   ```bash
   docker-compose up -d
   ```

5. **Access the application**:
   - Main form: http://localhost:5000
   - Admin dashboard: http://localhost:5000/admin
   - API health check: http://localhost:5000/api/health

### Environment Configuration

Required environment variables in `.env`:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=true
PORT=5000

# Airtable Configuration (REQUIRED)
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id

# LLM Configuration (Optional)
LLM_PROVIDER=openai  # or 'anthropic'
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Redis Configuration (Optional)
REDIS_URL=redis://redis:6379/0

# Application Settings
SHORTLIST_MIN_SCORE=2
RATE_LIMIT_PER_MINUTE=60
```

## API Documentation

### Endpoints

#### Application Submission
```http
POST /api/submit-application
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "location": "San Francisco, CA",
  "linkedin": "https://linkedin.com/in/johndoe",
  "work_experience": [
    {
      "company": "Tech Corp",
      "title": "Software Engineer",
      "start": "2021-01",
      "end": "present",
      "technologies": ["Python", "React", "PostgreSQL"]
    }
  ]
}
```

#### Get Shortlisted Candidates
```http
GET /api/shortlisted-leads?limit=50
```

#### Process Applicant
```http
POST /api/process-applicant/{applicant_id}
```

#### Get Applicant Details
```http
GET /api/applicant/{applicant_id}
```

#### Decompress Applicant Data
```http
POST /api/decompress-applicant/{applicant_id}
```

#### Health Check
```http
GET /api/health
```

## Database Schema

### Airtable Tables

#### Applicants Table
| Field Name | Type | Description |
|------------|------|-------------|
| Name | Single line text | Primary applicant name |
| Status | Single select | Application status (Pending, Processed) |
| Compressed JSON | Long text | Compressed applicant data |
| Last Hash | Single line text | Hash for change detection |
| LLM Summary | Long text | AI-generated summary |
| LLM Score | Number | AI evaluation score |

#### Personal Details Table
| Field Name | Type | Description |
|------------|------|-------------|
| Applicant Record | Link to Applicants | Reference to main record |
| Full Name | Single line text | Complete name |
| Email Address | Email | Contact email |
| City Location | Single line text | Location |
| LinkedIn Profile | URL | LinkedIn URL |

### Data Relationships

```
Applicants (1) ──────────── (1) Personal Details
     │
     │ (planned for future implementation)
     ├─────────── (n) Work Experience
     ├─────────── (1) Salary Preferences
     └─────────── (n) Shortlisted Leads
```

## Core Components

### 1. Airtable Client (`app/models/airtable_client.py`)

Handles all Airtable operations:
- CRUD operations for all tables
- Batch operations for efficiency
- Data validation and error handling
- Field mapping between application and database schema

Key methods:
- `create_applicant()`: Creates new applicant with linked records
- `get_applicant_data()`: Retrieves complete applicant information
- `list_records()`: General purpose record listing with filtering

### 2. JSON Compression (`app/models/compression.py`)

Implements efficient data compression:
- **Hash-based deduplication**: Only compress when data changes
- **Multiple algorithms**: gzip, bz2, lzma compression support
- **Base64 encoding**: Safe storage in text fields
- **Size optimization**: Automatic algorithm selection for best compression

Features:
- Change detection using SHA-256 hashes
- Automatic compression algorithm selection
- Memory-efficient processing
- Error recovery and validation

### 3. LLM Service (`app/models/llm_service.py`)

AI-powered candidate evaluation:
- **Multi-provider support**: OpenAI and Anthropic integration
- **Intelligent prompting**: Structured evaluation criteria
- **Usage tracking**: Token consumption and cost monitoring
- **Error handling**: Graceful fallback for API failures

Evaluation criteria:
- Technical skills assessment
- Experience relevance
- Communication quality
- Overall candidate fit

### 4. Shortlisting Engine (`app/models/shortlist_engine.py`)

Rule-based candidate ranking:
- **Configurable rules**: Flexible scoring criteria
- **Multiple rule types**: Experience, compensation, location, skills
- **Score calculation**: Weighted scoring with detailed reasoning
- **Automatic shortlisting**: Threshold-based candidate selection

Rule types supported:
- Experience-based rules (e.g., ">=3 years Python experience")
- Compensation rules (e.g., "<=100/hour rate")
- Location rules (e.g., "US only", "remote friendly")
- Technology rules (e.g., "has React experience")
- Availability rules (e.g., ">=40 hours/week")

### 5. Web Application (`app/main.py`)

Flask web server with:
- **RESTful API**: Complete CRUD operations
- **Rate limiting**: Configurable request throttling
- **Error handling**: Comprehensive error responses
- **Health monitoring**: System status endpoints
- **CORS support**: Cross-origin request handling

## User Interface

### Main Application Form (`/`)

Responsive form for candidate applications featuring:
- **Multi-step wizard**: Guided application process
- **Real-time validation**: Client-side form validation
- **Rich text areas**: Experience and skills description
- **File upload**: Resume and document support (planned)
- **Progress tracking**: Visual progress indicators

### Admin Dashboard (`/admin`)

Comprehensive management interface:
- **Statistics overview**: Key metrics and trends
- **Candidate listing**: Paginated candidate table
- **Filtering options**: Status, score, date filters
- **Bulk operations**: Mass candidate actions
- **Export functionality**: Data export capabilities

Dashboard features:
- Real-time statistics (total candidates, average scores)
- Interactive candidate table with sorting
- Modal dialogs for detailed candidate view
- One-click data decompression
- Auto-refresh every 30 seconds

## Development

### Project Structure

```
mercor-airtable/
├── app/
│   ├── main.py              # Flask application entry point
│   ├── models/              # Business logic models
│   │   ├── airtable_client.py    # Airtable integration
│   │   ├── compression.py        # JSON compression utilities
│   │   ├── llm_service.py        # AI evaluation service
│   │   └── shortlist_engine.py   # Candidate ranking system
│   └── templates/           # HTML templates
│       ├── base.html        # Base template
│       ├── index.html       # Application form
│       └── admin.html       # Admin dashboard
├── config/
│   └── settings.py          # Configuration management
├── tests/                   # Unit and integration tests
├── docker-compose.yml       # Container orchestration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── README.md              # Quick start guide
```

### Local Development Setup

1. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with development settings
   export FLASK_DEBUG=true
   ```

3. **Run locally**:
   ```bash
   cd app
   python main.py
   ```

### Hot Reloading

The Docker setup includes hot reloading for development:
- Code changes automatically restart the server
- Template changes reflect immediately
- No need to rebuild containers during development

### Testing

Run the test suite:
```bash
# In container
docker-compose exec app python -m pytest

# Locally
python -m pytest tests/
```

Test coverage includes:
- Unit tests for all core components
- Integration tests for API endpoints
- Airtable integration tests
- LLM service mocking and testing

## Configuration Options

### Application Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | dev-secret-key | Flask secret key for sessions |
| `FLASK_DEBUG` | False | Enable debug mode |
| `PORT` | 5000 | Application port |
| `MAX_JSON_SIZE` | 102400 | Maximum JSON size (100KB) |
| `SHORTLIST_MIN_SCORE` | 2 | Minimum score for shortlisting |
| `RATE_LIMIT_PER_MINUTE` | 60 | API rate limit |

### LLM Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_PROVIDER` | openai | LLM provider (openai/anthropic) |
| `LLM_MODEL` | gpt-4o-mini | Model to use |
| `LLM_MAX_TOKENS` | 512 | Maximum response tokens |

### Redis Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `REDIS_URL` | redis://redis:6379/0 | Redis connection string |

## Deployment

### Docker Production Deployment

1. **Build and deploy**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Environment setup**:
   - Use production-ready secret keys
   - Configure proper Redis instance
   - Set up SSL/TLS certificates
   - Configure reverse proxy (nginx recommended)

### Cloud Deployment Options

#### Heroku
```bash
heroku create your-app-name
heroku config:set AIRTABLE_API_KEY=your_key
heroku config:set AIRTABLE_BASE_ID=your_base
git push heroku main
```

#### AWS/GCP/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Configure environment variables in cloud console
- Set up managed Redis service for caching
- Configure load balancing for high availability

### Production Considerations

1. **Security**:
   - Use strong secret keys
   - Enable HTTPS only
   - Configure CORS properly
   - Implement authentication (planned feature)
   - Regular security updates

2. **Performance**:
   - Enable Redis caching
   - Configure proper rate limits
   - Use CDN for static assets
   - Monitor response times

3. **Monitoring**:
   - Set up application logging
   - Configure health check endpoints
   - Monitor API usage and errors
   - Track LLM usage costs

## Troubleshooting

### Common Issues

#### Airtable Connection Errors
```bash
# Check API key and base ID
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.airtable.com/v0/YOUR_BASE_ID/Applicants?maxRecords=1"
```

#### Redis Connection Issues
```bash
# Check Redis connectivity
docker-compose exec redis redis-cli ping
```

#### LLM API Errors
```bash
# Test OpenAI API
curl -H "Authorization: Bearer YOUR_OPENAI_KEY" \
  "https://api.openai.com/v1/models"
```

### Debug Mode

Enable debug mode for detailed error information:
```bash
export FLASK_DEBUG=true
docker-compose up
```

### Log Analysis

View application logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
```

## Performance Optimization

### Caching Strategy

1. **Redis Caching**:
   - API response caching
   - Rate limiting data
   - Session storage

2. **Application-level Caching**:
   - Airtable schema caching
   - LLM response caching
   - Compression dictionary caching

### Database Optimization

1. **Airtable Best Practices**:
   - Use appropriate field types
   - Minimize API calls with batch operations
   - Implement proper pagination
   - Cache frequently accessed data

2. **Query Optimization**:
   - Use filters to reduce data transfer
   - Implement proper indexing strategies
   - Batch related operations

## Security

### API Security

1. **Rate Limiting**: Configurable per-endpoint limits
2. **Input Validation**: Comprehensive data validation
3. **Error Handling**: Secure error responses
4. **CORS Configuration**: Proper cross-origin controls

### Data Security

1. **Encryption**: All data encrypted in transit and at rest
2. **Access Control**: API key-based authentication
3. **Data Validation**: Input sanitization and validation
4. **Audit Logging**: Comprehensive activity logging

## Future Enhancements

### Planned Features

1. **Authentication System**:
   - User registration and login
   - Role-based access control
   - OAuth integration

2. **Advanced Analytics**:
   - Candidate pipeline analytics
   - Performance metrics dashboard
   - Export and reporting tools

3. **Notification System**:
   - Email notifications for new applications
   - Slack/Teams integration
   - SMS notifications for urgent items

4. **Enhanced AI Features**:
   - Resume parsing and extraction
   - Skill matching algorithms
   - Predictive candidate success scoring

5. **Integration Capabilities**:
   - Webhook support for external systems
   - Calendar integration for interviews
   - Video interview scheduling

### Scaling Considerations

1. **Horizontal Scaling**:
   - Load balancer configuration
   - Multi-instance deployment
   - Database connection pooling

2. **Performance Monitoring**:
   - APM integration (New Relic, DataDog)
   - Custom metrics and alerting
   - Performance profiling

## Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run test suite: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Create Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Use type hints where applicable
- Maintain test coverage above 80%
- Document all public APIs
- Use meaningful commit messages

### Testing Guidelines

- Write unit tests for all new features
- Include integration tests for API endpoints
- Mock external services in tests
- Test error conditions and edge cases

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Review the troubleshooting section
- Check the API documentation
- Consult the Airtable setup guide

## Acknowledgments

- Built with Flask and Python
- Powered by Airtable for data storage
- AI capabilities by OpenAI and Anthropic
- UI components by Bootstrap
- Containerization by Docker

---

**Version**: 1.0.0  
**Last Updated**: August 2025  
**Repository**: https://github.com/jpete2477/mercor-airtable