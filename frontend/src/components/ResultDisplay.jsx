import React from 'react'
import './ResultDisplay.css'

/**
 * ResultDisplay Component
 * Shows the SQL query, data preview, and AI-generated summary
 */
const ResultDisplay = ({ result }) => {
  if (!result) return null

  return (
    <div className="result-display">
      {/* Generated SQL Query */}
      <section className="result-section">
        <h3>Generated SQL Query</h3>
        <pre className="sql-code">{result.sql_query}</pre>
      </section>

      {/* Data Preview */}
      {result.data_preview && result.data_preview.length > 0 && (
        <section className="result-section">
          <h3>Data Preview (Top 5 Rows)</h3>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  {Object.keys(result.data_preview[0]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.data_preview.map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).map((value, i) => (
                      <td key={i}>{value}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* AI Summary */}
      {result.summary && (
        <section className="result-section">
          <h3>AI Summary</h3>
          <p className="summary-text">{result.summary}</p>
        </section>
      )}

      {/* Status */}
      <div className="status-badge">
        Status: {result.status}
      </div>
    </div>
  )
}

export default ResultDisplay
