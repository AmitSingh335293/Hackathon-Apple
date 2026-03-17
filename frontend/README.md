# Frontend README

## NLP to SQL Analytics - React Frontend

This is the frontend application for the NLP to SQL Analytics system.

### Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **AWS Amplify** - Authentication (AWS Cognito)

### Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable React components
│   ├── pages/           # Page components
│   ├── services/        # API and service layers
│   ├── App.jsx          # Main app component
│   └── main.jsx         # Entry point
├── package.json
└── vite.config.js
```

### Getting Started

#### Prerequisites

- Node.js 18+ and npm

#### Installation

```bash
cd frontend
npm install
```

#### Development

```bash
npm run dev
```

The app will be available at http://localhost:3000

#### Build for Production

```bash
npm run build
```

The production build will be in the `build/` directory.

### Features (Placeholder)

- **Query Page**: Submit natural language questions
- **History Page**: View previous queries
- **Templates Page**: Browse query templates
- **Authentication**: AWS Cognito integration (to be implemented)

### Environment Variables

Copy `.env.example` to `.env.local` and configure:

```
VITE_API_URL=http://localhost:8000
```

### Docker

Build and run with Docker:

```bash
docker build -t nlp-sql-frontend .
docker run -p 3000:3000 nlp-sql-frontend
```

### TODO

- [ ] Implement AWS Cognito authentication
- [ ] Add real-time query execution status
- [ ] Implement query history pagination
- [ ] Add template search and filtering
- [ ] Add data visualization for results
- [ ] Add export functionality (CSV, JSON)
- [ ] Implement caching strategy
- [ ] Add error boundaries
- [ ] Add unit tests
- [ ] Add E2E tests
