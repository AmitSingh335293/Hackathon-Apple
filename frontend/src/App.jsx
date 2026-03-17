import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import QueryPage from './pages/QueryPage'
import HistoryPage from './pages/HistoryPage'
import TemplatesPage from './pages/TemplatesPage'
import Header from './components/Header'
import './App.css'

/**
 * Main App Component
 * Handles routing and layout for the NLP to SQL Analytics application
 */
function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<QueryPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/templates" element={<TemplatesPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
