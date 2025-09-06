import React, { useState, useEffect } from 'react'
import './App.css'
import TextAnalyzer from './components/TextAnalyzer'
import AnalysisList from './components/AnalysisList'
import SearchAnalyses from './components/SearchAnalyses'
import { API_ENDPOINTS } from './config'

function App() {
  const [activeTab, setActiveTab] = useState('analyze')
  const [analyses, setAnalyses] = useState([])

  const fetchAnalyses = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.LIST)
      if (response.ok) {
        const data = await response.json()
        setAnalyses(data)
      }
    } catch (error) {
      console.error('Error fetching analyses:', error)
    }
  }

  useEffect(() => {
    fetchAnalyses()
  }, [])

  const handleAnalysisCreated = (newAnalysis) => {
    setAnalyses(prev => [newAnalysis, ...prev])
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>🧠 AI Text Analyzer</h1>
        <p>Transform unstructured text into structured insights with AI-powered analysis</p>
      </header>

      <nav className="tab-navigation">
        <div className="tab-navigation-container">
          <button 
            className={activeTab === 'analyze' ? 'active' : ''}
            onClick={() => setActiveTab('analyze')}
          >
            Analyze Text
          </button>
          <button 
            className={activeTab === 'search' ? 'active' : ''}
            onClick={() => setActiveTab('search')}
          >
            Search
          </button>
          <button 
            className={activeTab === 'list' ? 'active' : ''}
            onClick={() => setActiveTab('list')}
          >
            All Analyses
          </button>
        </div>
      </nav>

      <main className="main-content">
        {activeTab === 'analyze' && (
          <TextAnalyzer onAnalysisCreated={handleAnalysisCreated} />
        )}
        {activeTab === 'search' && (
          <SearchAnalyses onSearchResults={setAnalyses} />
        )}
        {activeTab === 'list' && (
          <AnalysisList analyses={analyses} onRefresh={fetchAnalyses} />
        )}
      </main>
    </div>
  )
}

export default App