import React, { useState, useEffect } from 'react'
import { getTemplates } from '../services/api'
import './TemplatesPage.css'

/**
 * TemplatesPage Component
 * Displays and manages SQL query templates
 */
const TemplatesPage = () => {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      // TODO: Implement actual templates API call
      const data = await getTemplates()
      setTemplates(data)
    } catch (err) {
      console.error('Failed to load templates:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="templates-page">
      <div className="page-header">
        <h2>Query Templates</h2>
        <p>Pre-built SQL templates for common analytics questions</p>
      </div>

      {loading ? (
        <div className="loading">Loading templates...</div>
      ) : (
        <div className="templates-container placeholder-container">
          <p>Query templates will appear here</p>
          <p className="placeholder-text">
            This feature will show:
            <ul>
              <li>Pre-built SQL query templates</li>
              <li>Template parameters</li>
              <li>Usage examples</li>
              <li>Template performance metrics</li>
            </ul>
          </p>
          
          <div className="template-example">
            <h3>Example Template Structure</h3>
            <code>
              {`{
  "name": "revenue_by_region",
  "description": "Get revenue by region for a date range",
  "sql": "SELECT region, SUM(revenue) FROM apple_sales...",
  "parameters": ["start_date", "end_date"]
}`}
            </code>
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplatesPage
