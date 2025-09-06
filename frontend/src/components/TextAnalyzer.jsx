import React, { useState } from 'react'
import { API_ENDPOINTS } from '../config'

const TextAnalyzer = ({ onAnalysisCreated }) => {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!text.trim()) {
      setError('Please enter some text to analyze')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch(API_ENDPOINTS.ANALYZE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text.trim() }),
      })

      if (response.ok) {
        const analysis = await response.json()
        setSuccess('Text analyzed successfully!')
        setText('')
        onAnalysisCreated(analysis)
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Failed to analyze text')
      }
    } catch (err) {
      setError('Network error. Please check if the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Analyze Text</h2>
      <p style={{ marginBottom: '1.5rem', color: '#666' }}>
        Enter text below to get AI-powered analysis including summary, topics, sentiment, and keywords.
      </p>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="text">Text to Analyze</label>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter your text here... (e.g., article, blog post, or any content)"
            disabled={loading}
          />
        </div>

        <button 
          type="submit" 
          className="btn"
          disabled={loading || !text.trim()}
        >
          {loading ? (
            <>
              <span>Analyzing...</span>
              <div className="spinner" style={{
                width: '16px',
                height: '16px',
                border: '2px solid #ffffff',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
            </>
          ) : (
            'Analyze Text'
          )}
        </button>
      </form>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default TextAnalyzer
