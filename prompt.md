Prompt:

Context and Role
You are a senior full-stack software architect and principal engineer. You are responsible for designing and generating a complete production-grade Stock Market History and Live Price Checker Application using a modern scalable full-stack architecture.

Objective:

Develop a complete application that allows users to search live stock or commodity prices using a ticker symbol, and historical stock data using a ticker symbol and a previous date. The application must be production-ready, scalable, validated on both frontend and backend, and integrated with Yahoo Finance API.

Application Overview->
The application should support:

- Live stock/commodity search by ticker symbol only
- Historical stock search by ticker symbol and date
- “Market Closed” response when data does not exist for the selected date
- Prevention of future date selection
- Full request validation
- Clean UI and scalable backend architecture

Technology Stack->
Frontend:
- React
- Vite
- React Router
- Axios
- Tailwind CSS
- Context API or Redux Toolkit
- Recharts or Chart.js

Backend:
- Java 21
- Spring Boot 3+
- Maven
- REST APIs
- WebClient or RestTemplate
- Lombok
- Spring Validation
- Global Exception Handling
- Caching
- Logging

API:
- Yahoo Finance API / unofficial Yahoo Finance endpoints

Frontend Requirements:
- Responsive modern UI
- Dark/light mode
- Search bar
- Live Price button
- Historical Search button
- Date picker
- Validation messages
- Loading spinner
- Error alerts
- Stock cards
- Historical charts
- Search history
- Mobile responsive dashboard

Backend Requirements:
- REST APIs
- Service layer
- DTO layer
- Validation layer
- Exception handling
- Logging
- API response wrapper
- Rate limiting handling
- Retry mechanism
- Cache layer
- Clean architecture

Live Price Response
Return:
- ticker
- company name
- current price
- open
- high
- low
- previous close
- volume
- currency
- market state
- timestamp

Historical Data Response
Return:
- ticker
- date
- open
- high
- low
- close
- adjusted close
- volume

If no market data exists, return:
{
  "message": "Market Closed"
}

Validation Rules
Frontend:
- Empty ticker not allowed
- Future date not allowed
- Invalid ticker format handling
- Disable submit while loading

Backend:
- Validate ticker
- Validate date
- Reject future dates
- Proper HTTP status codes
- Prevent malformed requests

Error Handling
Handle:
- Invalid ticker
- Yahoo API failure
- Timeout
- Rate limit
- Network issues
- Null responses
- Invalid JSON
- Future date requests
- Market closed
- Internal server errors

Project Structure
Generate the complete folder structure for frontend and backend.
Include:
- every folder
- every file
- purpose of every file

Backend Deliverables
Generate:
- pom.xml
- application.yml
- controller classes
- service classes
- DTOs
- entities if needed
- utility classes
- exception classes
- config classes
- WebClient config
- logging config
- cache config
- validation classes
- API response wrapper
- scheduler if useful

Provide complete code with:
- imports
- annotations
- explanations

Backend APIs
1. GET /api/stocks/live/{ticker}
2. GET /api/stocks/history?ticker=AAPL&date=2024-05-10

Frontend Deliverables
Generate:
- complete React application
- Vite setup
- Tailwind setup
- routing
- API integration
- reusable components
- custom hooks
- context/redux store
- loading states
- error boundaries
- charts
- responsive UI
- all components
- all Tailwind/CSS code
- Axios service layer
- environment config

UI Requirements
Design should feel like a modern trading dashboard with:
- glassmorphism
- clean cards
- gradients
- smooth animations

Pages:
- Home page
- Live price page
- Historical data page
- Error page

Components:
- Navbar
- Footer
- Search form
- Stock card
- Historical table
- Loader
- Toast notifications
- Chart section

Security and Performance
Implement:
- CORS config
- Input sanitization
- API timeout handling
- Caching
- Debouncing
- Retry mechanism
- Optimized rendering
- Lazy loading

Testing
Generate:
- Backend unit tests
- Frontend tests
- API testing examples
- Postman collection

Docker Support
Generate:
- Dockerfile for frontend
- Dockerfile for backend
- docker-compose.yml

Deployment
Provide deployment steps for:
- Frontend on Vercel/Netlify
- Backend on Render/Railway/AWS

Documentation
Generate:
- README.md
- API documentation
- setup guide
- run instructions
- environment variables
- screenshots description

Output Format
Your response must include:
1. Complete system architecture
2. Full folder structure
3. All backend code
4. All frontend code
5. Step-by-step implementation
6. API integration details
7. Exception handling
8. Validation logic
9. Deployment guide
10. Testing guide
11. Docker setup
12. Scalability improvements
13. Future enhancements

Important Requirements
- Use clean code principles
- Use SOLID principles
- Use scalable architecture
- Use production-level practices
- Add comments in code
- Explain important sections
- Include all imports
- Do NOT skip any file
- Generate complete runnable code
- Ensure Java 21 compatibility
- Ensure React latest compatibility
- Use async handling properly
- Use centralized error handling
- Use DTOs instead of exposing raw models
- Follow REST best practices

Bonus Features
If possible, also include:
- Watchlist
- Favorite stocks
- Redis caching
- WebSocket live updates
- Pagination
- Search suggestions
- Swagger/OpenAPI docs
- JWT authentication
- User accounts
- Email alerts

Final Instruction
Now generate the complete application with detailed explanations and production-grade code.


