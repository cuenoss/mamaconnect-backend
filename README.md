# MamaConnect Backend

A comprehensive backend system for maternal health monitoring and care management, providing subscription plans, real-time health monitoring, midwife consultations, and pregnancy tracking.

## 🚀 Features

### Core Functionality
- **User Authentication & Authorization** with role-based access control
- **Subscription Management** with tiered pricing plans (Basic, Standard, Premium)
- **Real-time Health Monitoring** via wearable device integration
- **Midwife Consultations** with booking and verification system
- **Pregnancy Tracking** with personalized dashboards
- **Content Management** with articles and FAQs
- **Admin Panel** with comprehensive management tools

### Security Features
- JWT-based authentication
- Rate limiting and abuse prevention
- Input validation and sanitization
- Audit logging for sensitive operations
- Role-based permissions (User, Midwife, Admin)

## 📋 Prerequisites

### Required Software
1. **Python 3.8+**
2. **PostgreSQL** (for production database)
3. **pgAdmin** (database management tool)
4. **Redis** (for rate limiting and caching)
5. **Git** (version control)

### Database Setup

#### 1. Install PostgreSQL
```bash
# Windows
# Download and install from: https://www.postgresql.org/download/windows/

# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
```

#### 2. Install pgAdmin
```bash
# Windows
# Download and install from: https://www.pgadmin.org/download/windows.php

# macOS
brew install --cask pgadmin4

# Ubuntu/Debian
sudo apt-get install pgadmin4
```

#### 3. Create Database Server
1. **Open pgAdmin** and connect to your PostgreSQL server
2. **Create a new server** with these settings:
   - **Name**: MamaConnect Server
   - **Host**: localhost
   - **Port**: 5432
   - **Username**: postgres (or your PostgreSQL username)
   - **Password**: Your PostgreSQL password

3. **Create a new database**:
   - Right-click on your server → Create → Database
   - **Name**: mamaconnect
   - **Owner**: postgres (or your username)

#### 4. Configure Database Connection
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/mamaconnect
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379
```

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd mamaconnect-backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Redis (for rate limiting)
```bash
# Windows
# Download from: https://redis.io/download

# macOS
brew install redis

# Ubuntu/Debian
sudo apt-get install redis-server
```

### 5. Start Redis Server
```bash
# Windows
redis-server

# macOS/Linux
redis-server
```

## 🚀 Running the Application

### Development Mode
```bash
# Using Python module (recommended)
python -m uvicorn app.main:app --reload

# Alternative method
uvicorn app.main:app --reload
```

The application will be available at: **http://localhost:8000**

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
pytest tests/test_auth_routes.py
pytest tests/test_client_routes.py
pytest tests/test_profile_routes.py
pytest tests/test_articles_routes.py
pytest tests/test_midwife_routes.py
pytest tests/test_admin_routes.py
```

### Run Tests with Coverage
```bash
pytest --cov=app tests/
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Security Tests**: Authentication and authorization validation

## 📊 Database Schema

### Core Tables
- **users**: User accounts and profiles
- **plans**: Subscription plans and pricing
- **subscriptions**: User subscription records
- **bookings**: Midwife appointment bookings
- **articles**: Health content and articles
- **faqs**: Frequently asked questions
- **chat_sessions**: AI chatbot conversations
- **monitoring_logs**: Health monitoring data

### Relationships
- Users → Subscriptions (one-to-many)
- Users → Bookings (one-to-many)
- Midwives → Bookings (one-to-many)
- Plans → Subscriptions (one-to-many)

## 🔧 Configuration

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/mamaconnect

# Security
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379

# Application
DEBUG=True
CORS_ORIGINS=["http://localhost:3000"]
```

## 📡 API Endpoints

### Authentication (`/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `GET /me` - Get current user

### Client Routes (`/client/*`)
- `GET /dashboard/pregnancy-info` - Pregnancy dashboard
- `GET /monitoring/belt` - Health monitoring data
- `POST /monitoring/belt/data` - Submit sensor data
- `GET /booking/midwives` - List available midwives
- `POST /booking/` - Create appointment
- `GET /subscription/plans` - View subscription plans
- `POST /subscription/subscribe` - Subscribe to plan

### Midwife Routes (`/midwife/*`)
- `GET /profile` - Midwife profile
- `PUT /profile` - Update profile
- `POST /license` - Add professional license
- `GET /bookings` - View appointments
- `PUT /bookings/{id}` - Update booking status

### Admin Routes (`/admin/*`)
- `GET /dashboard` - Admin dashboard
- `GET /users` - User management
- `POST /midwives/{id}/approve` - Verify midwife
- `GET /analytics/*` - System analytics
- `POST /articles` - Content management

## 🔒 Security Features

### Authentication
- JWT-based token authentication
- Role-based access control (User, Midwife, Admin)
- Token expiration and refresh

### Rate Limiting
- Redis-based rate limiting
- Per-user and per-endpoint limits
- Configurable time windows

### Input Validation
- Pydantic schema validation
- SQL injection prevention
- XSS protection

### Audit Logging
- Subscription changes
- Admin actions
- Security events

## 🚀 Deployment

### Production Setup
1. **Environment Configuration**:
   ```env
   DEBUG=False
   DATABASE_URL=postgresql://user:pass@prod-host:5432/mamaconnect
   SECRET_KEY=production-secret-key
   ```

2. **Database Migration**:
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

3. **Start Production Server**:
   ```bash
   # Using Gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   
   # Or using Docker
   docker-compose up -d
   ```

### Docker Deployment
```bash
# Build image
docker build -t mamaconnect-backend .

# Run container
docker run -p 8000:8000 mamaconnect-backend
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `pytest`
5. Commit changes: `git commit -m "Add feature"`
6. Push to branch: `git push origin feature-name`
7. Create Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive tests
- Document new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

#### Database Connection Errors
1. Ensure PostgreSQL is running
2. Check database credentials in `.env`
3. Verify database exists in pgAdmin

#### Redis Connection Errors
1. Start Redis server: `redis-server`
2. Check Redis URL in `.env`
3. Verify Redis is installed correctly

#### Test Failures
1. Install test dependencies: `pip install pytest httpx`
2. Check database connection for tests
3. Verify all fixtures are properly configured

### Getting Help
- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issue with detailed description
- **Support**: Contact development team

## 📈 Monitoring & Analytics

### Application Monitoring
- Health check endpoints
- Performance metrics
- Error tracking
- User analytics

### Database Monitoring
- Connection pool monitoring
- Query performance
- Index optimization

---

**Built with ❤️ for maternal health and wellness**
