# ZeroGuard AI - DevOps Configuration Intelligence Platform

ZeroGuard AI is a comprehensive AI-powered platform for analyzing and securing DevOps configurations. It provides intelligent insights into Dockerfiles, docker-compose.yml files, and environment configurations using advanced AI analysis and security scanning.

## 🚀 Features

### 🔍 Core Analysis Capabilities
- **Root-Cause Tracing**: AI-powered analysis to explain WHY deployments fail
- **Multi-File Cross Analysis**: Detect port conflicts, undefined dependencies, version mismatches
- **Security Scanning**: Integration with Hadolint and Trivy for comprehensive security analysis
- **Secret Leakage Detection**: Hybrid regex + AI confirmation for sensitive data detection
- **Auto-Fix Generation**: AI-generated fixes with confidence scores
- **Deployment Risk Scoring**: Comprehensive risk assessment with breakdown metrics

### 📊 Advanced Features
- **Deployment Simulation**: Heuristic analysis of build stability, runtime stability, and security posture
- **Visual Dependency Graph**: Interactive service dependency visualization with React Flow
- **Infrastructure Best Practices**: Automated detection of DevOps best practice violations
- **AI Explainability**: Beginner and DevOps modes for different expertise levels
- **Comprehensive Reporting**: Detailed reports with exportable JSON format

### 🎨 Professional Dashboard
- **Dark Theme**: Modern SaaS interface with responsive design
- **Real-time Analysis**: Live scanning with progress indicators
- **Interactive Visualizations**: Risk meters, charts, and dependency graphs
- **AI Assistant**: Context-aware chat interface for questions and explanations

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **AI Engine**: OpenAI integration for intelligent analysis
- **Validator**: Syntax and logic validation for configurations
- **Security Scanner**: Hadolint and Trivy integration
- **Secret Scanner**: Regex patterns with AI confirmation
- **Risk Scoring**: Comprehensive risk assessment algorithms
- **Simulation Engine**: Deployment simulation and prediction
- **Dependency Graph**: Service relationship analysis

### Frontend (React + Vite)
- **Modern UI**: Tailwind CSS with dark theme
- **Interactive Components**: Upload, Dashboard, Reports, AI Assistant
- **Visualizations**: Chart.js and React Flow for data presentation
- **Responsive Design**: Mobile-friendly interface

## 📋 Prerequisites

### Required Tools
- Python 3.8+
- Node.js 16+
- Docker (for security scanning)
- Hadolint (recommended)
- Trivy (recommended)

### Optional External Tools
- Docker Desktop
- Git

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hackathonhem
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# or with yarn
yarn install
```

### 4. Environment Configuration

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Running the Application

### 1. Start Backend Server

```bash
# In backend directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Start Frontend Development Server

```bash
# In frontend directory
npm run dev

# or with yarn
yarn dev
```

The application will be available at `http://localhost:3000`

## 📖 Usage Guide

### 1. Upload Configuration Files
- Navigate to "Upload & Scan" section
- Upload your Dockerfile, docker-compose.yml, and optionally .env files
- Choose analysis mode: Beginner or DevOps
- Click "Start Analysis"

### 2. Review Analysis Results
- **Dashboard**: Overview with risk meter, issue summary, and AI explanations
- **Dependency Graph**: Visual representation of service relationships
- **Security Issues**: Detailed security vulnerability analysis
- **Best Practices**: Recommendations for improvement
- **Secret Detection**: Identified sensitive data

### 3. Generate Reports
- Navigate to "Report" section
- Filter and search through issues
- Export detailed analysis as JSON

### 4. AI Assistant
- Ask questions about your configuration
- Get explanations for specific issues
- Receive personalized recommendations

## 🔧 Configuration

### Backend Configuration
- `OPENAI_API_KEY`: Required for AI analysis
- `CORS_ORIGINS`: Configure allowed frontend origins
- `SCAN_TIMEOUT`: Adjust timeout for long-running scans

### Frontend Configuration
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)
- Theme and display settings in `tailwind.config.js`

## 📊 API Endpoints

### Main Endpoints
- `POST /scan` - Analyze configuration files
- `POST /explain` - Get AI explanation for specific issues
- `GET /` - Health check

### Scan Response Format
```json
{
  "syntax_errors": [],
  "security_issues": [],
  "logic_conflicts": [],
  "secrets_detected": [],
  "best_practices": [],
  "suggested_fixes": [],
  "confidence_scores": [],
  "ai_explanation": "",
  "simulation_scores": {},
  "dependency_graph": {
    "nodes": [],
    "edges": []
  },
  "risk_score": {
    "overall": 0,
    "level": "Low/Medium/High",
    "breakdown": {}
  }
}
```

## 🛡️ Security Features

### Scanning Capabilities
- **Hadolint Integration**: Dockerfile best practices and security
- **Trivy Integration**: Container image vulnerability scanning
- **Regex Pattern Matching**: 20+ secret detection patterns
- **AI Confirmation**: Machine learning validation of suspected secrets

### Risk Assessment
- **Multi-dimensional Scoring**: Syntax, security, logic, and secret risks
- **Confidence Metrics**: AI confidence levels for all detections
- **Deployment Simulation**: Predictive analysis of deployment success

## 🎯 Best Practices

### For Optimal Performance
- Use specific version tags instead of `latest`
- Implement proper secret management
- Follow Dockerfile best practices
- Configure resource limits in docker-compose
- Add health checks to services

### Security Recommendations
- Regularly scan configurations
- Rotate exposed credentials
- Use environment-specific files
- Implement proper access controls
- Monitor dependency updates

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues
- **ModuleNotFoundError**: Ensure virtual environment is activated
- **OpenAI API errors**: Check API key configuration
- **Docker scan failures**: Ensure Docker is running and accessible

#### Frontend Issues
- **CORS errors**: Check backend CORS configuration
- **API connection errors**: Verify backend is running on correct port
- **Build errors**: Clear node_modules and reinstall dependencies

#### Tool Integration
- **Hadolint not found**: Install via `npm install -g hadolint`
- **Trivy not found**: Install from https://github.com/aquasecurity/trivy
- **Docker permission issues**: Ensure user has Docker permissions

### Debug Mode
Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Add comprehensive error handling
- Include unit tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Hadolint for Dockerfile linting
- Trivy for security scanning
- React Flow for dependency visualization
- Tailwind CSS for styling

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**ZeroGuard AI** - Your intelligent DevOps configuration companion 🛡️✨
