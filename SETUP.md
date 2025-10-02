# AI Cybersecurity Honeypot - Setup Guide

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Node.js 18+** (for local development)
- **Python 3.9+** (for local development)
- **Git** (for cloning the repository)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/letroy969/ai-cybersecurity-honeypot.git
   cd ai-cybersecurity-honeypot
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Wait for services to initialize** (2-3 minutes)

4. **Access the dashboard**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

5. **Generate synthetic attacks**
   ```bash
   docker-compose exec backend python tools/gen_attacks.py --count 50
   ```

### Option 2: Local Development Setup

1. **Clone and setup backend**
   ```bash
   git clone https://github.com/letroy969/ai-cybersecurity-honeypot.git
   cd ai-cybersecurity-honeypot/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Setup database**
   ```bash
   # Install PostgreSQL locally or use Docker
   docker run -d --name honeypot-db -e POSTGRES_PASSWORD=honeypot_password -p 5432:5432 postgres:15
   ```

3. **Initialize database**
   ```bash
   python -c "from database.connection import init_database; init_database()"
   ```

4. **Start backend**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Setup frontend** (in another terminal)
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://honeypot_user:honeypot_password@localhost:5432/honeypot_db

# Redis
REDIS_URL=redis://localhost:6379

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Docker Configuration

The `docker-compose.yml` file includes:
- **PostgreSQL**: Primary database
- **Redis**: Caching and sessions
- **Elasticsearch**: Search and analytics
- **Kibana**: Data visualization
- **Backend**: FastAPI application
- **Frontend**: React dashboard
- **ML Service**: Machine learning processing

## Usage Guide

### 1. Accessing the Dashboard

1. Open http://localhost:3000 in your browser
2. You'll see the security dashboard with:
   - Real-time attack statistics
   - Geographic attack distribution
   - Attack timeline visualization
   - Top attackers analysis

### 2. Generating Test Data

```bash
# Generate 100 synthetic attacks
python tools/gen_attacks.py --count 100

# Generate specific attack types
python tools/gen_attacks.py --type sql --count 50
python tools/gen_attacks.py --type xss --count 30

# Real-time attack simulation
python tools/gen_attacks.py --real-time --duration 10 --interval 30
```

### 3. Exploring Honeypot Endpoints

The system includes several simulated vulnerable endpoints:

- **Login Portal**: http://localhost:8000/api/honeypots/login
- **SQL Interface**: http://localhost:8000/api/honeypots/sql
- **File Access**: http://localhost:8000/api/honeypots/file
- **Admin Panel**: http://localhost:8000/api/honeypots/admin
- **Configuration**: http://localhost:8000/api/honeypots/config

### 4. API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## Testing the System

### 1. Manual Testing

Try these attack patterns against the honeypot endpoints:

```bash
# SQL Injection
curl "http://localhost:8000/api/honeypots/sql?query=1%20UNION%20SELECT%20*%20FROM%20users"

# XSS
curl "http://localhost:8000/api/honeypots/search?q=<script>alert('xss')</script>"

# Directory Traversal
curl "http://localhost:8000/api/honeypots/file?path=../../../etc/passwd"

# Brute Force
curl -X POST "http://localhost:8000/api/honeypots/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 2. Automated Testing

```bash
# Run the attack generator
python tools/gen_attacks.py --count 100 --real-time

# Check dashboard for results
# Open http://localhost:3000 and observe the attack data
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check all services
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs frontend

# Database health
docker-compose exec backend python -c "from database.connection import get_db_connection; print(get_db_connection())"
```

### Backup and Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U honeypot_user honeypot_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U honeypot_user honeypot_db < backup.sql
```

### Performance Monitoring

- **System Metrics**: http://localhost:8000/api/health/metrics
- **Application Logs**: Check `docker-compose logs`
- **Database Performance**: Use pgAdmin or similar tools

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep :3000
   netstat -tulpn | grep :8000
   ```

2. **Database Connection Issues**
   ```bash
   # Restart database
   docker-compose restart postgres
   
   # Check database logs
   docker-compose logs postgres
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear node modules and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **ML Model Issues**
   ```bash
   # Retrain models
   docker-compose exec backend python -m ml.anomaly_detector --retrain
   ```

### Log Locations

- **Backend Logs**: `docker-compose logs backend`
- **Frontend Logs**: `docker-compose logs frontend`
- **Database Logs**: `docker-compose logs postgres`
- **Application Logs**: Inside containers at `/app/logs/`

### Performance Issues

1. **High Memory Usage**
   - Reduce Docker memory limits
   - Optimize ML model parameters
   - Clear old data regularly

2. **Slow Response Times**
   - Check database indexes
   - Optimize ML feature extraction
   - Use Redis caching effectively

## Security Considerations

### ⚠️ Important Security Notes

1. **Educational Use Only**: This system is for learning and research
2. **No Real Data**: All data is synthetic and simulated
3. **Isolated Environment**: Keep the system in isolated networks
4. **Regular Updates**: Keep dependencies updated
5. **Access Control**: Implement proper authentication for production use

### Network Security

```bash
# Only expose necessary ports
docker-compose down
# Edit docker-compose.yml to remove unnecessary port mappings
docker-compose up -d
```

### Data Privacy

- All IP addresses are synthetic
- No real personal data is collected
- Data can be cleared anytime
- Regular data purging recommended

## Advanced Configuration

### Custom ML Models

```python
# Train custom models
from ml.anomaly_detector import AnomalyDetector

detector = AnomalyDetector()
await detector.train_models()
```

### Custom Honeypot Endpoints

```python
# Add new endpoints in backend/api/routes/honeypots.py
@router.get("/custom")
async def custom_honeypot(request: Request):
    # Your custom honeypot logic here
    pass
```

### Dashboard Customization

```typescript
// Customize dashboard in frontend/src/pages/Dashboard.tsx
// Add new components in frontend/src/components/
```

## Support and Contributing

### Getting Help

1. **Documentation**: Check `/docs/` folder
2. **Issues**: Report on GitHub Issues
3. **Discussions**: Use GitHub Discussions

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Add tests for new features
- Update documentation
- Follow security best practices

## License and Legal

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

**⚠️ Legal Notice**: This is for educational purposes only. Do not use in production environments without proper authorization and legal compliance.

---

For more information, see the [README.md](README.md) and [LEGAL.md](LEGAL.md) files.
