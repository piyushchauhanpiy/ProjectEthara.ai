# Stock Market History & Live Price Checker

Production-grade full-stack application for live stock/commodity quotes and historical OHLC data, powered by Yahoo Finance unofficial APIs.

## Architecture

```
React (Vite + Tailwind)  →  Spring Boot REST API  →  Yahoo Finance
         │                           │
         │                    Caffeine Cache
         └──── localStorage: history, watchlist, theme
```

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, React Router, Axios, Tailwind, Recharts, Context API, react-hot-toast |
| Backend | Java 21, Spring Boot 3.2, WebFlux WebClient, Validation, Caffeine Cache, Spring Retry, Actuator, OpenAPI |
| DevOps | Docker, docker-compose, Nginx |

## Project Structure

```
stock-market-app/
├── backend/                 # Spring Boot API
│   ├── src/main/java/com/stockmarket/
│   │   ├── config/          # WebClient, Cache, CORS, OpenAPI
│   │   ├── controller/      # REST endpoints
│   │   ├── dto/             # Request/response models
│   │   ├── exception/       # Global error handling
│   │   ├── integration/     # Yahoo Finance client
│   │   ├── service/         # Business logic + parsing
│   │   └── util/            # Ticker & date validation
│   └── src/test/            # Unit tests
├── frontend/                # React SPA
│   └── src/
│       ├── components/      # UI components
│       ├── context/         # Theme, history, watchlist
│       ├── hooks/           # useDebounce
│       ├── pages/           # Home, Live, Historical, 404
│       └── services/        # Axios API layer
├── docker-compose.yml
├── golden_response.py       # Standalone Python replica (Stockstracker)
├── postman/                 # API collection
└── README.md
```

## API Endpoints

### Live Price
```
GET /api/stocks/live/{ticker}
```
Example: `GET /api/stocks/live/AAPL`

Response:
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "companyName": "Apple Inc.",
    "currentPrice": 210.55,
    "open": 208.0,
    "high": 212.3,
    "low": 207.4,
    "previousClose": 206.1,
    "volume": 72829282,
    "currency": "USD",
    "marketState": "REGULAR",
    "timestamp": 1717500000
  },
  "timestamp": "2026-05-25T12:00:00Z"
}
```

### Historical Data
```
GET /api/stocks/history?ticker=AAPL&date=2024-05-10
```

Success: wrapped `data` with OHLC fields.

Market closed (weekend/holiday):
```json
{ "message": "Market Closed" }
```

## Quick Start

### Prerequisites
- Java 21+
- Maven 3.9+
- Node.js 20+

### Backend
```bash
cd backend
# Use mvnw if Maven is not installed globally (Windows):
.\mvnw.cmd spring-boot:run
# Or, if mvn is on your PATH:
mvn spring-boot:run
```
API: http://localhost:8080  
Swagger: http://localhost:8080/swagger-ui.html

### Frontend
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
App: http://localhost:5173

### Docker (full stack)
```bash
docker compose up --build
```
- Frontend: http://localhost  
- Backend: http://localhost:8080

### Standalone Python Replica (Stockstracker)

Alternatively, you can run the entire application (both the backend API and the interactive dashboard) using a zero-dependency Python script:

1. **Start the server**:
   ```bash
   python golden_response.py
   ```
2. **Access the application**:
   - Interactive Dashboard: [http://localhost:8080](http://localhost:8080) (or `http://localhost:8081` if port 8080 is occupied)
   - Live Stock API: `http://localhost:8080/api/stocks/live/AAPL`
   - Historical API: `http://localhost:8080/api/stocks/history?ticker=AAPL&date=2024-05-10`

## Environment Variables

| Variable | Location | Default |
|----------|----------|---------|
| `VITE_API_BASE_URL` | frontend/.env | `http://localhost:8080/api/stocks` |
| `app.cors.allowed-origins` | backend application.yml | `http://localhost:5173` |
| `app.yahoo-finance.base-url` | backend application.yml | Yahoo query1 API |

## Testing

### Backend
```bash
cd backend
mvn test
```

### Frontend
```bash
cd frontend
npm test
```

### Postman
Import `postman/Stock-Market-API.postman_collection.json`.

### cURL Examples
```bash
curl http://localhost:8080/api/stocks/live/AAPL
curl "http://localhost:8080/api/stocks/history?ticker=AAPL&date=2024-05-10"
curl "http://localhost:8080/api/stocks/history?ticker=AAPL&date=2024-05-11"
```

## Deployment

### Frontend (Vercel / Netlify)
1. Root directory: `frontend`
2. Build: `npm run build`
3. Output: `dist`
4. Env: `VITE_API_BASE_URL=https://your-api.com/api/stocks`

### Backend (Render / Railway / AWS)
1. Root: `backend`
2. Build: `mvn clean package -DskipTests`
3. Start: `java -jar target/stock-backend-1.0.0.jar`
4. Set `APP_CORS_ALLOWED_ORIGINS` to your frontend URL

## Features

- Live quotes for stocks and commodities (`GC=F`, `CL=F`)
- Historical OHLC by date with **Market Closed** detection
- Future date rejection (client + server)
- Caffeine caching (1 min live / 24h historical)
- Retry on Yahoo API failures
- Dark/light mode, search history, watchlist
- Glassmorphism trading dashboard UI
- OpenAPI/Swagger documentation
- Global exception handling with proper HTTP codes

## Scalability Improvements

- Replace Caffeine with Redis for multi-instance deployments
- Fully reactive stack (remove `.block()` in service)
- API gateway rate limiting (Bucket4j)
- Circuit breaker (Resilience4j)
- PostgreSQL for search analytics
- WebSocket for live price streaming

## License

MIT
