import React, { useState } from 'react'
import QueryInput from '../components/QueryInput'
import ResultDisplay from '../components/ResultDisplay'
import { submitQuery } from '../services/api'
import './QueryPage.css'

/**
 * QueryPage Component
 * Main page for submitting natural language queries
 */
const QueryPage = () => {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (query) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // TODO: Replace with actual user ID from AWS Cognito
      const response = await submitQuery({
        user_id: 'demo_user',
        query: query
      })
      setResult(response)
    } catch (err) {
      setError(err.message || 'Failed to process query')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="query-page">
      <div className="page-header">
        <h2>Ask a Question</h2>
        <p>Convert your natural language questions into SQL queries</p>
      </div>

      <QueryInput onSubmit={handleSubmit} loading={loading} />

      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Processing your query...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
        </div>
      )}

      {result && <ResultDisplay result={result} />}
    </div>
  )
}

export default QueryPage
