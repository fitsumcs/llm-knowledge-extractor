# LLM Knowledge Extractor

A full-stack application that uses OpenAI's GPT to analyze text and extract structured insights including summaries, topics, sentiment, and keywords.

## Features

- **Text Analysis**: Submit any text for AI-powered analysis
- **Structured Data Extraction**: 
  - 1-2 sentence summary
  - Title extraction
  - 3 key topics
  - Sentiment analysis (positive/neutral/negative)
  - 3 most frequent nouns as keywords
  - Confidence score (0.0 to 1.0)
- **Search & Filter**: Search through stored analyses by topic, keyword, or sentiment
- **Batch Processing**: Analyze up to 10 texts at once
- **Confidence Scoring**: Get confidence scores for analysis quality
- **Fallback Mode**: Works without OpenAI API key using intelligent mock analysis
- **Modern UI**: Clean, responsive React frontend with Vite
- **RESTful API**: Django REST Framework backend
- **Comprehensive Testing**: Unit and integration tests included

## 🤖 AI Analysis Modes

The application supports two analysis modes with automatic fallback:

### **OpenAI Mode (Primary)**
- **When**: OpenAI API key is configured and has available credits
- **Quality**: High-quality, context-aware analysis using GPT-3.5-turbo
- **Features**: 
  - Intelligent summarization
  - Context-aware topic extraction
  - Accurate sentiment analysis
  - High confidence scores (0.8-1.0)
- **Cost**: ~$0.001-0.01 per analysis (depending on text length)

### **Mock Mode (Fallback)**
- **When**: OpenAI API key is missing, invalid, or quota exceeded
- **Quality**: Rule-based analysis using predefined patterns
- **Features**:
  - Pattern-based summarization
  - Predefined topic categories
  - Keyword-based sentiment analysis
  - Moderate confidence scores (0.4-0.8)
- **Cost**: Free (no API calls)
- **Use Cases**: 
  - Development and testing
  - Demonstrations
  - When OpenAI credits are exhausted
  - Offline usage

### **Automatic Fallback**
The system automatically detects API issues and falls back to mock mode, ensuring the application always works. You'll see clear logging indicating which mode is being used.

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework, SQLite
- **Frontend**: React 18, Vite
- **AI**: OpenAI GPT-3.5-turbo
- **NLP**: NLTK for keyword extraction

## Project Structure

```
llm-knowledge-extractor/
├── backend/                 # Django REST API
│   ├── llm_extractor/      # Django project settings
│   ├── analyzer/           # Main app with models, views, utils
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│ 
├── frontend/               # React + Vite app
│   ├── src/
│   │   ├── components/     # React components
│   │   └── App.jsx
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml      # Docker orchestration
├── env.example      # Environment template
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional - app works with fallback mode)

### Setup and Run

1. **Clone and navigate to the project**:
   ```bash
   git clone <your-repo-url>
   cd llm-knowledge-extractor
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start the application**:
   ```bash
   docker compose up -d --build
   ```

4. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000/api/
   - **API Documentation**: http://localhost:8000/api/docs/

5. **Monitor the logs** (optional):
   ```bash
   # View backend logs to see which analysis mode is being used
   docker compose logs backend -f
   
   # You'll see messages like:
   # 🤖 Attempting to use OpenAI API...
   # ✅ Successfully used OpenAI API for analysis
   # OR
   # ⚠️ OpenAI API error: quota exceeded
   # 🔄 Falling back to mock analyzer...
   ```

### Stop the application:
```bash
docker compose down
```

## Local Development (Optional)

If you prefer to run without Docker:

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run database migrations**:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

5. **Start the Django server**:
   ```bash
   python3 manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

## API Endpoints

- `POST /api/analyze/` - Analyze new text
- `POST /api/batch-analyze/` - Analyze multiple texts at once (max 10)
- `GET /api/search/` - Search analyses (query params: topic, keyword, sentiment)
- `GET /api/list/` - List all analyses
- `GET /api/{id}/` - Get specific analysis

## 🔄 Fallback System

The application includes an intelligent fallback system that ensures it always works:

- **Automatic Detection**: If OpenAI API key is missing, invalid, or quota exceeded, the system automatically switches to mock analysis
- **Realistic Data**: Mock analyzer generates realistic summaries, titles, topics, and sentiment based on text content
- **Keyword Extraction**: Real keyword extraction using NLTK (works regardless of API key)
- **Confidence Scoring**: Adjusted confidence scores for mock analysis (capped at 0.8)
- **Method Indication**: API responses include `analysis_method` field showing "openai" or "mock"
- **Clear Logging**: Console shows which mode is being used with emoji indicators

This allows you to test and demonstrate the application logic without requiring an OpenAI API key.

## ⚖️ Tradeoffs & When to Use Each Mode

### **Choose OpenAI Mode When:**
- **Production use** - You need high-quality analysis
- **Accuracy matters** - Context-aware insights are important
- **Budget available** - You have OpenAI credits
- **Real-world data** - Analyzing actual user content

### **Choose Mock Mode When:**
- **Development/Testing** - Building and testing features
- **Demonstrations** - Showing the system to stakeholders
- **Budget constraints** - No OpenAI credits available
- **Offline usage** - Working without internet access
- **Learning purposes** - Understanding the system architecture

### **Hybrid Approach:**
The automatic fallback system gives you the best of both worlds:
- **Primary**: OpenAI for production quality
- **Fallback**: Mock for reliability and cost control
- **Transparent**: Clear indication of which mode is active

## API Documentation

The API includes comprehensive Swagger/OpenAPI documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

The documentation includes:
- Interactive API testing
- Request/response examples
- Parameter descriptions
- Error code explanations
- Try-it-out functionality


## Design Choices

I chose Django REST Framework for the backend because it provides excellent built-in serialization, validation, and API documentation features. The modular structure with separate apps makes the codebase maintainable and scalable.

For the frontend, I selected Vite over Create React App for its superior performance and faster development experience. The component-based architecture with separate files for each feature (analyze, search, list) ensures good separation of concerns.

Docker containerization provides consistent environments across development and production, with separate configurations for development (hot reload) and production (optimized builds). The multi-stage Docker build for the frontend optimizes the final image size.

The keyword extraction uses NLTK with part-of-speech tagging to identify nouns, which is more accurate than simple word frequency counting. Error handling is implemented at both API and UI levels to gracefully handle edge cases like empty input and API failures.

## Trade-offs Made

Due to the 2-hour time constraint, I focused on core functionality over advanced features. I used SQLite instead of PostgreSQL for simplicity, and implemented basic error handling rather than comprehensive logging. The UI is functional but could benefit from more advanced styling and animations.

## Usage

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in your browser
3. Use the "Analyze Text" tab to submit text for analysis
4. Use the "Search" tab to find specific analyses
5. Use the "All Analyses" tab to view all stored analyses

## Error Handling

The application handles:
- Empty text input
- OpenAI API failures
- Network connectivity issues
- Invalid search parameters

All errors are displayed to the user with helpful messages.
