import React from 'react'

const AnalysisList = ({ analyses, onRefresh }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const getSentimentClass = (sentiment) => {
    return `sentiment-${sentiment}`
  }

  if (analyses.length === 0) {
    return (
      <div className="card">
        <div className="empty-state">
          <h3>No analyses yet</h3>
          <p>Start by analyzing some text using the "Analyze Text" tab.</p>
          <button className="btn" onClick={onRefresh} style={{ marginTop: '1rem' }}>
            Refresh
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2>All Analyses ({analyses.length})</h2>
        <button className="btn btn-secondary" onClick={onRefresh}>
          Refresh
        </button>
      </div>

      <div>
        {analyses.map((analysis) => (
          <div key={analysis.id} className="analysis-card">
            <div className="analysis-title">
              {analysis.title || 'Untitled Analysis'}
            </div>
            
            <div className="analysis-summary">
              {analysis.summary}
            </div>

            <div className="analysis-meta">
              <div className={`meta-item ${getSentimentClass(analysis.sentiment)}`}>
                <span>Sentiment:</span>
                <strong>{analysis.sentiment}</strong>
              </div>
              <div className="meta-item confidence-item" title="Analysis confidence score (0-100%)">
                <span>Confidence:</span>
                <div className="confidence-display">
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${analysis.confidence_score * 100}%` }}
                    ></div>
                  </div>
                  <strong>{Math.round(analysis.confidence_score * 100)}%</strong>
                </div>
              </div>
              <div className="meta-item" title={analysis.analysis_method === 'openai' ? 'Analyzed using OpenAI AI' : 'Analyzed using fallback mock system'}>
                <span>Method:</span>
                <strong className={analysis.analysis_method === 'openai' ? 'method-openai' : 'method-mock'}>
                  {analysis.analysis_method === 'openai' ? 'AI' : 'Mock'}
                </strong>
              </div>
              <div className="meta-item">
                <span>Created:</span>
                <strong>{formatDate(analysis.created_at)}</strong>
              </div>
            </div>

            {analysis.topics && analysis.topics.length > 0 && (
              <div>
                <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#333' }}>Topics:</strong>
                <div className="topics-keywords">
                  {analysis.topics.map((topic, index) => (
                    <span key={index} className="topic-tag">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {analysis.keywords && analysis.keywords.length > 0 && (
              <div>
                <strong style={{ display: 'block', marginBottom: '0.5rem', marginTop: '1rem', color: '#333' }}>Keywords:</strong>
                <div className="topics-keywords">
                  {analysis.keywords.map((keyword, index) => (
                    <span key={index} className="keyword-tag">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <details style={{ marginTop: '1rem' }}>
              <summary style={{ cursor: 'pointer', color: '#667eea', fontWeight: '500' }}>
                View Original Text
              </summary>
              <div style={{ 
                marginTop: '0.5rem', 
                padding: '1rem', 
                background: '#f8f9fa', 
                borderRadius: '8px',
                fontSize: '0.9rem',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap'
              }}>
                {analysis.original_text}
              </div>
            </details>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AnalysisList
