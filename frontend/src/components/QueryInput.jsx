import React, { useState } from 'react'
import './QueryInput.css'

/**
 * QueryInput Component
 * Text input for natural language questions
 */
const QueryInput = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSubmit(query)
    }
  }

  return (
    <div className="query-input-container">
      <form onSubmit={handleSubmit}>
        <textarea
          className="query-textarea"
          placeholder="Ask a question... (e.g., What was iPhone revenue in India last quarter?)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          disabled={loading}
        />
        <button 
          type="submit" 
          className="submit-button"
          disabled={loading || !query.trim()}
        >
          {loading ? 'Processing...' : 'Ask Question'}
        </button>
      </form>
    </div>
  )
}

export default QueryInput
