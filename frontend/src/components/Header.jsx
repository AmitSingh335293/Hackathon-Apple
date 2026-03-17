import React from 'react'
import { Link } from 'react-router-dom'
import './Header.css'

/**
 * Header Component
 * Navigation bar for the application
 */
const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <h1 className="logo">NLP to SQL Analytics</h1>
        <nav className="nav">
          <Link to="/" className="nav-link">Query</Link>
          <Link to="/history" className="nav-link">History</Link>
          <Link to="/templates" className="nav-link">Templates</Link>
        </nav>
        <div className="user-section">
          {/* Placeholder for user authentication */}
          <span className="user-name">User</span>
        </div>
      </div>
    </header>
  )
}

export default Header
