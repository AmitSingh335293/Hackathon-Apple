import React, { useState, useEffect } from 'react'
import { getQueryHistory } from '../services/api'
import './HistoryPage.css'

/**
 * HistoryPage Component
 * Displays query history for the current user
 */
const HistoryPage = () => {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    try {
      // TODO: Implement actual history API call
      const data = await getQueryHistory('demo_user')
      setHistory(data)
    } catch (err) {
      console.error('Failed to load history:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="history-page">
      <div className="page-header">
        <h2>Query History</h2>
        <p>View your previous queries and results</p>
      </div>

      {loading ? (
        <div className="loading">Loading history...</div>
      ) : (
        <div className="history-container placeholder-container">
          <p>Query history will appear here</p>
          <p className="placeholder-text">
            This feature will show:
            <ul>
              <li>Previous natural language questions</li>
              <li>Generated SQL queries</li>
              <li>Query execution time</li>
              <li>Result summaries</li>
            </ul>
          </p>
        </div>
      )}
    </div>
  )
}

export default HistoryPage
