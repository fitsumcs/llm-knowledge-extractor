from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import TextAnalysis
from .utils import analyze_text_complete


class TextAnalysisModelTest(TestCase):
    def test_text_analysis_creation(self):
        """Test creating a TextAnalysis instance"""
        analysis = TextAnalysis.objects.create(
            original_text="Test text about AI and machine learning",
            summary="A brief summary about AI",
            title="AI Test",
            topics=["artificial intelligence", "machine learning", "technology"],
            sentiment="positive",
            keywords=["AI", "learning", "technology"]
        )
        
        self.assertEqual(analysis.original_text, "Test text about AI and machine learning")
        self.assertEqual(analysis.sentiment, "positive")
        self.assertEqual(len(analysis.topics), 3)
        self.assertEqual(len(analysis.keywords), 3)


class TextAnalysisAPITest(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.analyze_url = reverse('analyze_text')
        self.list_url = reverse('list_analyses')
        self.search_url = reverse('search_analyses')
        
        # Create test analysis
        self.test_analysis = TextAnalysis.objects.create(
            original_text="Test text about technology",
            summary="A summary about technology",
            title="Technology Test",
            topics=["technology", "innovation", "future"],
            sentiment="positive",
            keywords=["technology", "innovation", "future"]
        )

    @patch('analyzer.utils.LLMAnalyzer')
    def test_analyze_text_success(self, mock_llm_class):
        """Test successful text analysis"""
        # Mock the LLM analyzer to return specific data
        mock_llm_instance = mock_llm_class.return_value
        mock_llm_instance.analyze_text.return_value = {
            'summary': 'Test summary',
            'title': 'Test Title',
            'topics': ['topic1', 'topic2', 'topic3'],
            'sentiment': 'positive'
        }
        
        data = {'text': 'This is a test text about artificial intelligence'}
        response = self.client.post(self.analyze_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['summary'], 'Test summary')
        self.assertEqual(response.data['sentiment'], 'positive')
        self.assertEqual(response.data['analysis_method'], 'openai')

    def test_analyze_text_empty_input(self):
        """Test analysis with empty text"""
        data = {'text': ''}
        response = self.client.post(self.analyze_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_analyses(self):
        """Test listing all analyses"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Technology Test')

    def test_search_analyses_by_topic(self):
        """Test searching analyses by topic"""
        response = self.client.get(self.search_url, {'topic': 'technology'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_analyses_by_sentiment(self):
        """Test searching analyses by sentiment"""
        response = self.client.get(self.search_url, {'sentiment': 'positive'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_analyses_no_params(self):
        """Test search without parameters"""
        response = self.client.get(self.search_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_analysis_by_id(self):
        """Test getting specific analysis by ID"""
        url = reverse('get_analysis', kwargs={'analysis_id': self.test_analysis.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.test_analysis.id)

    def test_get_analysis_not_found(self):
        """Test getting non-existent analysis"""
        url = reverse('get_analysis', kwargs={'analysis_id': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TextAnalysisUtilsTest(TestCase):
    @patch('analyzer.utils.LLMAnalyzer')
    @patch('analyzer.utils.KeywordExtractor')
    def test_analyze_text_complete(self, mock_keyword_class, mock_llm_class):
        """Test complete text analysis function"""
        # Mock LLM analyzer
        mock_llm_instance = mock_llm_class.return_value
        mock_llm_instance.analyze_text.return_value = {
            'summary': 'Test summary',
            'title': 'Test Title',
            'topics': ['topic1', 'topic2', 'topic3'],
            'sentiment': 'positive'
        }
        
        # Mock keyword extractor
        mock_keyword_instance = mock_keyword_class.return_value
        mock_keyword_instance.extract_keywords.return_value = ['keyword1', 'keyword2', 'keyword3']
        
        result = analyze_text_complete('Test text about AI')
        
        self.assertEqual(result['summary'], 'Test summary')
        self.assertEqual(result['sentiment'], 'positive')
        self.assertEqual(len(result['topics']), 3)
        self.assertEqual(len(result['keywords']), 3)
        self.assertEqual(result['analysis_method'], 'openai')

    def test_analyze_text_complete_empty_input(self):
        """Test analyze_text_complete with empty input"""
        with self.assertRaises(ValueError):
            analyze_text_complete('')
    
    @patch('analyzer.utils.LLMAnalyzer')
    @patch('analyzer.utils.KeywordExtractor')
    def test_analyze_text_fallback_mode(self, mock_keyword_class, mock_llm_class):
        """Test fallback to mock analyzer when OpenAI fails"""
        # Mock LLM analyzer to raise an exception
        mock_llm_class.side_effect = ValueError("OpenAI API key not configured")
        
        # Mock keyword extractor
        mock_keyword_instance = mock_keyword_class.return_value
        mock_keyword_instance.extract_keywords.return_value = ['test', 'fallback', 'system']
        
        result = analyze_text_complete('Test text for fallback mode')
        
        self.assertEqual(result['analysis_method'], 'mock')
        self.assertIn('summary', result)
        self.assertIn('title', result)
        self.assertIn('topics', result)
        self.assertIn('sentiment', result)
        self.assertEqual(len(result['keywords']), 3)
        self.assertLess(result['confidence_score'], 0.8)  # Mock analysis has lower confidence
