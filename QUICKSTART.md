# Quick Start Guide

Get the NLP to SQL Analytics System (Full Stack) running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher and npm
- Optional: Docker & Docker Compose

---

## Option 1: Docker Compose (Recommended)

The easiest way to run both frontend and backend:

```bash
# Navigate to project directory
cd Hackathon-Apple

# Build and start all services
docker-compose up --build

# Access the application:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

To stop the services:
```bash
docker-compose down
```

---

## Option 2: Manual Setup

### Step 1: Setup Backend

```bash
# Navigate to project directory
cd Hackathon-Apple

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# The default settings work for local testing (MOCK_MODE=true)

# Start the backend server
python -m uvicorn app.main:app --reload
```

Backend will be running at http://localhost:8000

### Step 2: Setup Frontend

Open a new terminal window:

```bash
# Navigate to frontend directory
cd Hackathon-Apple/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local if needed (default values work for local setup)

# Start the development server
npm run dev
```

Frontend will be running at http://localhost:3000

---

## Step 3: Test the Application
```

## Step 4: Test the API

Open your browser and visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Try Your First Query

Using the interactive docs at `/docs`:

1. Navigate to `POST /api/v1/ask`
2. Click "Try it out"
3. Use this example request:

```json
{
  "user_id": "test_user",
  "query": "What was iPhone revenue in India last quarter?",
  "auto_execute": true
}
```

4. Click "Execute"
5. See the SQL query, results, and AI-generated summary!

### Or use curl:

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "query": "What was iPhone revenue in India last quarter?",
    "auto_execute": true
  }'
```

## Step 5: Try More Queries

Here are some example queries to try:

- "Show me revenue by region last quarter"
- "What are the top products by sales?"
- "Compare iPhone and iPad revenue"
- "Show revenue trend by month for Mac"
- "What was total revenue in 2024?"

## Docker Quick Start (Alternative)

If you prefer Docker:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the API at http://localhost:8000
```

## What's Happening?

In **MOCK MODE** (default), the system:
- Uses simulated LLM responses (no AWS required)
- Executes queries on local CSV data
- Generates mock embeddings for template matching

This lets you test the full functionality without AWS credentials!

## Next Steps

### For Development:
- Explore the code in `app/`
- Add new query templates in `data/templates/query_templates.json`
- Modify mock data in `data/mock/apple_sales_fact.csv`

### For AWS Deployment:
1. Get AWS credentials with Bedrock access
2. Update `.env` with your AWS credentials
3. Set `MOCK_MODE=false`
4. Configure Athena, OpenSearch, and other services
5. Run deployment script: `./scripts/deploy.sh`

## Common Issues

### Port 8000 already in use
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

### Module not found errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Permission denied on scripts
```bash
chmod +x scripts/*.sh
```

## Getting Help

- Check the main [README.md](README.md) for full documentation
- Review [API documentation](docs/API.md) for endpoint details
- Open an issue on GitHub

## Success! 🎉

You now have a working NLP to SQL system. Start asking questions in natural language and let AI convert them to SQL!
