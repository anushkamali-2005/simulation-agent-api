# Simulation Agent API

REST API for testing and evaluating medical AI models through clinical simulations.

## 🚀 Quick Start

### Local Development
```bash
pip install -r requirements-api.txt
python run_api.py
```

Visit: http://localhost:8000/docs

### Cloud Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📡 API Endpoints

- `GET /api/simulation/health` - Health check
- `POST /api/simulation/generate-questions` - Generate clinical questions
- `POST /api/simulation/load-benchmarks` - Load benchmark answers
- `POST /api/simulation/compare-answers` - Compare model vs benchmark answers
- `POST /api/simulation/run` - Run complete simulation workflow

## 📚 Documentation

- **Usage Guide**: [API_USAGE.md](API_USAGE.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Interactive Docs**: http://localhost:8000/docs (when running)

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation**: Pydantic v2
- **Python**: 3.11+

## 📄 License

MIT
