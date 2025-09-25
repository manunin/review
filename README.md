# Review Analysis Platform 🔍✨

> Task-based API for sentiment analysis with asynchronous processing and modern web interface

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-35495E?logo=vue.js)](https://vuejs.org/)

## 📋 Project Overview

**Review Analysis Platform** is a modern web application for sentiment analysis of text reviews. The system implements a task-based architecture with asynchronous processing, allowing users to analyze single reviews or batch process files, with real-time status updates and comprehensive results.

### 🎯 Key Features

- **Task-Based Architecture**: Asynchronous processing with status tracking (accepted → queued → ready)
- **Single Text Analysis**: Real-time sentiment analysis of individual reviews
- **Batch File Processing**: Upload and analyze CSV, TXT, JSON files with multiple reviews
- **Real-Time Polling**: Frontend automatically polls for task completion with UI blocking
- **Mock Worker System**: Background worker for simulating ML processing pipeline
- **PostgreSQL Database**: Persistent storage with comprehensive task tracking
- **Docker Ready**: Full containerization with docker-compose setup
- **OpenAPI Compliant**: Comprehensive API documentation with Swagger UI

## 🚀 Technology Stack

### Backend
- **Python 3.11** - Modern Python with async support
- **FastAPI** - High-performance async web framework
- **SQLAlchemy 2.0** - Modern ORM with async support
- **Alembic** - Database migrations
- **Pydantic** - Data validation and serialization
- **Mock Worker** - Background task processing simulation

### Frontend  
- **Vue.js 3** - Modern reactive framework with Composition API
- **Vite** - Fast build tool and dev server
- **PrimeVue** - Comprehensive UI component library
- **Pinia** - State management for Vue 3
- **TypeScript** - Type-safe development
- **Axios** - HTTP client for API communication

### Database & Infrastructure
- **PostgreSQL 15** - Reliable relational database
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and static file serving

### Architecture Patterns
- **Task-Based Processing** - Asynchronous job processing
- **Domain-Driven Design** - Clear separation of concerns
- **Repository Pattern** - Data access abstraction
- **Composable Pattern** - Reusable UI logic (Vue 3)

## 📦 Installation and Setup

### Prerequisites

```bash
# Docker and Docker Compose
docker --version
docker-compose --version

# For local development (optional):
# Python 3.11+
python --version

# Node.js 18+ (for frontend development)
node --version
```

### Quick Start with Docker

```bash
# Clone repository
git clone https://github.com/manunin/review.git
cd review

# Copy environment configuration
cp .env.example .env

# Build and start all services
make docker-up
# or manually:
# docker-compose up --build -d

# Check services status
docker-compose ps
```

The application will be available at:
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

### Local Development Setup

#### Backend Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL required)
cp .env.example .env
# Edit DATABASE_URL in .env

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit VITE_API_BASE_URL if needed

# Start development server
npm run dev
```

### Available Make Commands

```bash
# Docker operations
make docker-up          # Build and start all services
make docker-down        # Stop and remove containers
make docker-logs        # View logs from all services
make docker-rebuild     # Rebuild and restart services

# Development
make lint               # Run code linting
make format             # Format code
make test               # Run tests
make check-db           # Check database connection

# Database utilities
make migrate            # Run database migrations
make db-shell           # Access PostgreSQL shell
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=review_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Docker Environment
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/review_db

# Local Development (override for local development)
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/review_db

# API Settings
DEBUG=false
SECRET_KEY=your-super-secret-key-change-in-production
API_VERSION=v1

# File Upload Limits
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_FILE_TYPES=csv,txt,json

# Mock Worker Settings
WORKER_ENABLED=true
WORKER_DELAY_SECONDS=5
```

### Frontend Configuration (.env in frontend/)

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Development settings
VITE_DEBUG_MODE=false
```

## 📊 Usage

### 1. Single Text Analysis

1. Navigate to http://localhost:3001
2. Enter text in the "Single Review Analysis" section
3. Click "Analyze" - the interface will block input during processing
4. Results appear automatically after ~5 seconds with sentiment and confidence

### 2. Batch File Analysis

1. Use the "Batch File Analysis" section
2. Upload a supported file (CSV, TXT, JSON)
3. Supported formats:
   - **CSV**: Reviews in rows/columns
   - **TXT**: One review per line
   - **JSON**: Array of review objects
4. Maximum file size: 10MB
5. Interface shows processing status with polling updates
6. View comprehensive statistics when complete

### 3. API Usage

#### Single Text Analysis
```bash
# Submit analysis task
curl -X POST http://localhost:8000/api/v1/task/run/single \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "text": "Great product, highly recommended!"}'

# Get result
curl -X POST http://localhost:8000/api/v1/task/result/single \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

#### Batch File Analysis
```bash
# Submit batch task
curl -X POST http://localhost:8000/api/v1/task/run/batch \
  -F "user_id=user123" \
  -F "file=@reviews.csv"

# Get result
curl -X POST http://localhost:8000/api/v1/task/result/batch \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

## 🔄 Task Processing Architecture

### Task Lifecycle

```
User Request → accepted → queued → ready
                ↓           ↓        ↓
            API Response  Worker   Result
```

### Mock Worker System

The current implementation uses a mock worker to simulate ML processing:

1. **Task Creation**: Tasks start with `accepted` status
2. **Queue Processing**: Mock worker moves tasks to `queued` status
3. **Processing Delay**: 5-second delay simulates ML processing time
4. **Result Generation**: Mock results with realistic sentiment scores
5. **Completion**: Tasks marked as `ready` with results stored in database

### Background Worker

```python
# Mock worker provides:
- Sentiment classification (positive/negative/neutral)
- Confidence scores (0.0 - 1.0)
- Batch statistics (percentages, counts)
- Error handling and status updates
```

### Real-Time Updates

- Frontend polls every 5 seconds during processing
- UI blocks input fields while tasks are processing
- Automatic result display when tasks complete
- Error handling with user-friendly messages

## 📈 API Documentation

### Task Execution Endpoints

#### Single Text Analysis
```bash
# Create single analysis task
POST /api/v1/task/run/single
{
  "user_id": "string",
  "text": "string (max 512 chars)"
}

# Get single task result
POST /api/v1/task/result/single
{
  "user_id": "string"
}
```

#### Batch File Analysis
```bash
# Create batch analysis task
POST /api/v1/task/run/batch
Content-Type: multipart/form-data
- user_id: string
- file: file (CSV/TXT/JSON, max 10MB)

# Get batch task result  
POST /api/v1/task/result/batch
{
  "user_id": "string"
}
```

#### System Endpoints
```bash
# Health check
GET /health

# API root info
GET /

# OpenAPI schema
GET /api/v1/openapi.json
```

### Response Schemas

#### Task Response
```json
{
  "task_id": "uuid",
  "type": "single|batch", 
  "status": "accepted|queued|ready|error",
  "start": 1234567890,
  "end": 1234567890,
  "result": {...},
  "error": null
}
```

#### Single Result
```json
{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.85,
  "text": "analyzed text"
}
```

#### Batch Result
```json
{
  "total_reviews": 150,
  "positive": 90,
  "negative": 35, 
  "neutral": 25,
  "positive_percentage": 60.0,
  "negative_percentage": 23.3,
  "neutral_percentage": 16.7
}
```

**Full interactive API documentation**: http://localhost:8000/docs

## 🧪 Testing & Development

### Code Quality

```bash
# Linting and formatting
make lint           # Run flake8, mypy, etc.
make format         # Format code with black, isort

# Testing
make test           # Run pytest suite
pytest --cov=app    # Run with coverage

# Database utilities
make migrate        # Run Alembic migrations
make db-shell       # Access PostgreSQL shell
./app/utils/check_tasks.sh  # Check tasks in database
```

### Development Workflow

```bash
# 1. Start services
make docker-up

# 2. Check logs
make docker-logs

# 3. Make changes to code

# 4. Rebuild affected services
docker-compose build backend  # For backend changes
docker-compose build frontend # For frontend changes

# 5. Restart services
docker-compose up -d backend
```

### Debugging

```bash
# View backend logs
docker-compose logs -f backend

# View frontend logs  
docker-compose logs -f frontend

# Check database tasks
./app/utils/check_tasks.sh

# Access container shells
docker exec -it review-backend-1 bash
docker exec -it review-frontend-1 sh
docker exec -it review-postgres-1 psql -U postgres -d review_db
```

## 📁 Project Structure

```
review/
├── app/                        # Backend application (FastAPI)
│   ├── core/                  # Configuration, logging, exceptions
│   ├── infra/                 # Infrastructure layer
│   │   └── db/               # Database models, repositories
│   ├── tasks/                 # Task domain
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── router.py         # API endpoints
│   │   └── service.py        # Business logic
│   ├── workers/              # Background workers
│   │   └── mock_worker.py    # Mock ML processing worker
│   ├── utils/                # Utilities
│   │   └── check_tasks.sh    # Database inspection script
│   └── main.py               # FastAPI application entry
├── frontend/                   # Vue.js 3 application
│   ├── src/
│   │   ├── components/       # Vue components
│   │   ├── views/            # Page components (Upload.vue)
│   │   ├── store/            # Pinia stores
│   │   ├── services/         # API services  
│   │   ├── composables/      # Vue 3 composables (useTaskPolling)
│   │   ├── types/            # TypeScript type definitions
│   │   └── mocks/            # Mock data for development
│   ├── nginx.conf            # Nginx configuration
│   └── Dockerfile            # Frontend container build
├── data/                      # Sample data files
├── docs/                      # Documentation
├── alembic/                   # Database migrations
├── docker-compose.yml         # Multi-service container setup
├── Dockerfile.backend         # Backend container build
├── docker-entrypoint.sh       # Backend startup script
├── Makefile                   # Development automation
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation
```

## 🐳 Docker Architecture

### Services

- **Backend** (port 8000): FastAPI application with mock worker
- **Frontend** (port 3001): Vue.js SPA served by Nginx
- **PostgreSQL** (port 5432): Database with persistent volume

### Container Management

```bash
# Start all services
make docker-up
# or: docker-compose up --build -d

# Stop services
make docker-down  
# or: docker-compose down

# View logs
make docker-logs
# or: docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Access service shells
docker exec -it review-backend-1 bash
docker exec -it review-postgres-1 psql -U postgres -d review_db
```

### Volumes & Data Persistence

- PostgreSQL data persists in Docker volume `postgres_data`
- Backend code mounted for development
- Frontend build artifacts served by Nginx

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React
- Test coverage should be at least 80%
- Document new features

## 📋 Roadmap

### v1.0 (Current - MVP)
- ✅ Task-based architecture with async processing
- ✅ Single text and batch file analysis
- ✅ Real-time UI updates with polling
- ✅ Mock worker system for development
- ✅ Docker containerization
- ✅ OpenAPI compliant REST API
- ✅ Vue.js 3 modern frontend
- ✅ PostgreSQL data persistence

### v1.1 (Planned - ML Integration)
- 🔄 Real ML model integration (replace mock worker)
- 🔄 Model training pipeline
- 🔄 Enhanced sentiment confidence scoring
- 🔄 Multi-language support
- 🔄 Result export functionality (CSV, JSON)

### v2.0 (Future - Advanced Features) 
- 📋 Aspect-based sentiment analysis
- 📋 Emotion detection (joy, sadness, anger, etc.)
- 📋 Real-time analysis via WebSockets
- 📋 User authentication and multi-tenancy
- 📋 Advanced analytics dashboard
- 📋 API rate limiting and caching
- 📋 Kubernetes deployment manifests

## ⚠️ Known Limitations

- **Mock Processing**: Currently uses simulated ML processing (not real AI models)
- **Text Length**: Single reviews limited to 512 characters
- **File Size**: Batch files limited to 10MB
- **Concurrent Users**: No user authentication - single-user simulation with user_id
- **File Formats**: Limited to CSV, TXT, JSON (no Excel, PDF, etc.)
- **Languages**: Mock worker returns English results only
- **Scalability**: Single worker process (not horizontally scalable yet)

## �️ Troubleshooting

### Common Issues

**Frontend can't connect to backend:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify docker services
docker-compose ps

# Check frontend environment
cat frontend/.env
```

**Database connection issues:**
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Verify database exists
docker exec review-postgres-1 psql -U postgres -l
```

**Tasks not processing:**
```bash
# Check worker logs
docker-compose logs backend | grep worker

# Inspect tasks in database
./app/utils/check_tasks.sh
```

### Performance Notes

- Processing delay is intentionally set to 5 seconds for demo purposes
- Real ML models would have variable processing times
- Database queries are optimized with indexes for user_id and status

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the existing code style and architecture patterns
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

### Development Guidelines

- Follow FastAPI and Vue.js best practices
- Use TypeScript for frontend development
- Write comprehensive docstrings for Python code
- Maintain clean separation between UI logic (composables) and state (Pinia stores)
- Test API endpoints with the included utilities

---

⭐ **If this project helped you, please give it a star on GitHub!**

**Made with ❤️ for modern web development**
