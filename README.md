# AI Cybersecurity Honeypot 🛡️

A sophisticated, educational cybersecurity honeypot system that simulates vulnerable endpoints, collects attacker telemetry, and uses machine learning to classify and predict attacker behaviors. Features a polished dashboard for security analysis and incident reporting.

## 🎯 Overview

This project demonstrates advanced security engineering, machine learning, and UX design capabilities by creating a comprehensive honeypot ecosystem that:

- **Simulates vulnerable endpoints** to attract and study attacker behaviors
- **Collects comprehensive telemetry** from all interactions
- **Uses ML anomaly detection** to identify suspicious patterns
- **Provides real-time dashboards** for security analysis
- **Generates automated reports** on attack techniques and trends

## ⚠️ Legal & Ethical Notice

**THIS IS FOR EDUCATIONAL PURPOSES ONLY**

- 🚫 **DO NOT** deploy to production or public internet
- 🚫 **DO NOT** use against real systems without authorization
- ✅ Designed for local testing and learning environments only
- ✅ All attack simulations use synthetic data
- ✅ Includes comprehensive legal documentation

See [LEGAL.md](./LEGAL.md) for complete terms and conditions.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Honeypot      │    │   Telemetry     │    │   ML Pipeline   │
│   Endpoints     │───▶│   Ingestion     │───▶│   Analysis      │
│   (Flask/FastAPI│    │   (PostgreSQL)  │    │   (PyTorch)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Attack        │    │   Event         │    │   Dashboard     │
│   Simulation    │    │   Storage       │    │   (React+MUI)   │
│   (Synthetic)   │    │   (ELK Stack)   │    │   Visualization │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ 
- Python 3.9+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/letroy969/ai-cybersecurity-honeypot.git
   cd ai-cybersecurity-honeypot
   ```

2. **Start the system**
   ```bash
   docker-compose up -d
   ```

3. **Access the dashboard**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Database: localhost:5432

4. **Generate synthetic attacks**
   ```bash
   python tools/gen_attacks.py --count 100
   ```

## 📊 Features

### 🎣 Honeypot Endpoints
- **Fake Login Portal** - Simulates common web vulnerabilities
- **API Endpoints** - RESTful services with intentional weaknesses
- **SSH Honeypot** - Simulated shell access attempts
- **Database Honeypot** - SQL injection detection

### 🧠 ML Anomaly Detection
- **Isolation Forest** - Unsupervised anomaly detection
- **Autoencoder** - Deep learning pattern recognition
- **Attack Classification** - Categorizes threat types
- **Behavioral Analysis** - User fingerprinting and profiling

### 📈 Dashboard & Analytics
- **Real-time Attack Map** - Geographic visualization
- **Timeline Analysis** - Attack sequence replay
- **Incident Cards** - Detailed threat information
- **Automated Reports** - PDF/HTML generation

### 🔒 Security Features
- **Containerized Environment** - Isolated local network
- **Data Redaction** - Privacy protection
- **Rate Limiting** - DoS protection
- **Audit Logging** - Complete activity tracking

## 🛠️ Tech Stack

### Backend
- **Python 3.9+** - Core application logic
- **Flask/FastAPI** - Web framework and API
- **PostgreSQL** - Primary data storage
- **Redis** - Caching and session management
- **PyTorch** - Machine learning models

### Frontend
- **React 18** - User interface framework
- **Material-UI (MUI)** - Component library
- **Framer Motion** - Animations and transitions
- **Recharts** - Data visualization
- **TypeScript** - Type safety

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Elasticsearch** - Search and analytics
- **Kibana** - Data visualization
- **Prometheus** - Monitoring and metrics

## 📁 Project Structure

```
ai-cybersecurity-honeypot/
├── backend/
│   ├── api/              # REST API endpoints
│   ├── ml/               # Machine learning models
│   ├── telemetry/        # Data ingestion pipeline
│   └── honeypots/        # Vulnerable endpoint simulations
├── frontend/
│   ├── src/              # React application
│   └── public/           # Static assets
├── tools/
│   ├── gen_attacks.py    # Synthetic attack generator
│   └── data_export.py    # Data export utilities
├── docs/
│   ├── architecture.md   # System design documentation
│   ├── api.md           # API documentation
│   └── case_study.md    # Usage examples and analysis
├── reports/              # Generated incident reports
├── demo/                 # Demo data and scripts
├── tests/                # Unit and integration tests
└── docker-compose.yml    # Container orchestration
```

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Frontend Tests
```bash
cd frontend && npm test
```

### End-to-End Demo
```bash
python demo/run_demo.py
```

## 📊 Sample Data & Reports

The project includes synthetic attack data and automated report generation:

- **Attack Patterns** - Common techniques and TTPs
- **Geographic Distribution** - IP geolocation analysis
- **Timeline Analysis** - Attack sequence reconstruction
- **Threat Intelligence** - IOCs and indicators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Sihle Dladla (letroy969)**
- 🎓 ICT Diploma final-year student at University of Mpumalanga
- 💻 Building real-world projects for portfolio
- 📫 Contact: Lindaletroy27@gmail.com
- 🌍 Based in Nelspruit, South Africa

## 🙏 Acknowledgments

- Security research community for attack pattern data
- Open source ML libraries and frameworks
- Educational cybersecurity resources
- Docker and containerization community

---

**⚠️ Remember: This is for educational purposes only. Use responsibly and ethically.**
