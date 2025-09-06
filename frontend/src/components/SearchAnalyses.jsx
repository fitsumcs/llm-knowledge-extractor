import React, { useState } from 'react'
import AnalysisList from './AnalysisList'
import { API_ENDPOINTS } from '../config'

const SearchAnalyses = ({ onSearchResults }) => {
  const [searchParams, setSearchParams] = useState({
    topic: '',
    keyword: '',
    sentiment: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState([])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    
    // Check if at least one search parameter is provided
    if (!searchParams.topic && !searchParams.keyword && !searchParams.sentiment) {
      setError('Please provide at least one search parameter')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Build query string
      const params = new URLSearchParams()
      if (searchParams.topic) params.append('topic', searchParams.topic)
      if (searchParams.keyword) params.append('keyword', searchParams.keyword)
      if (searchParams.sentiment) params.append('sentiment', searchParams.sentiment)

      const response = await fetch(`${API_ENDPOINTS.SEARCH}?${params.toString()}`)

      if (response.ok) {
        const data = await response.json()
        setResults(data)
        onSearchResults(data)
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Search failed')
      }
    } catch (err) {
      setError('Network error. Please check if the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setSearchParams({
      topic: '',
      keyword: '',
      sentiment: ''
    })
    setResults([])
    setError('')
  }

  return (
    <div>
      <div className="card">
        <h2>Search Analyses</h2>
        <p style={{ marginBottom: '1.5rem', color: '#666' }}>
          Search through your stored analyses by topic, keyword, or sentiment.
        </p>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSearch}>
          <div className="search-form">
            <div className="form-group">
              <label htmlFor="topic">Topic</label>
              <input
                type="text"
                id="topic"
                name="topic"
                value={searchParams.topic}
                onChange={handleInputChange}
                placeholder="e.g., technology, health, business"
              />
            </div>

            <div className="form-group">
              <label htmlFor="keyword">Keyword</label>
              <input
                type="text"
                id="keyword"
                name="keyword"
                value={searchParams.keyword}
                onChange={handleInputChange}
                placeholder="e.g., AI, climate, innovation"
              />
            </div>

            <div className="form-group">
              <label htmlFor="sentiment">Sentiment</label>
              <select
                id="sentiment"
                name="sentiment"
                value={searchParams.sentiment}
                onChange={handleInputChange}
              >
                <option value="">Any sentiment</option>
                <option value="positive">Positive</option>
                <option value="neutral">Neutral</option>
                <option value="negative">Negative</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              type="submit" 
              className="btn"
              disabled={loading}
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={loading}
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      {results.length > 0 && (
        <div className="card">
          <h3>Search Results ({results.length})</h3>
          <AnalysisList analyses={results} onRefresh={() => {}} />
        </div>
      )}

      {results.length === 0 && !loading && (searchParams.topic || searchParams.keyword || searchParams.sentiment) && (
        <div className="card">
          <div className="empty-state">
            <h3>No results found</h3>
            <p>Try adjusting your search parameters or check the spelling.</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default SearchAnalyses
