import re
import json
import random
import openai
from collections import Counter
from typing import List, Dict, Any
from django.conf import settings
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class MockAnalyzer:
    """
    Fallback analyzer that generates realistic sample data when OpenAI is unavailable
    """
    def __init__(self):
        self.sample_topics = [
            ["technology", "innovation", "digital"],
            ["health", "wellness", "medical"],
            ["business", "economy", "finance"],
            ["education", "learning", "knowledge"],
            ["environment", "sustainability", "climate"],
            ["science", "research", "discovery"],
            ["culture", "society", "community"],
            ["art", "creativity", "design"],
            ["travel", "adventure", "exploration"],
            ["food", "cooking", "nutrition"]
        ]
        
        self.sentiment_keywords = {
            "positive": ["excellent", "amazing", "great", "wonderful", "fantastic", "outstanding", "brilliant", "superb", "incredible", "remarkable"],
            "negative": ["terrible", "awful", "horrible", "disappointing", "frustrating", "concerning", "problematic", "difficult", "challenging", "negative"],
            "neutral": ["standard", "typical", "normal", "regular", "common", "usual", "average", "moderate", "standard", "conventional"]
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Generate mock analysis data based on text content
        """
        # Extract first few words for title
        words = text.split()[:5]
        title = " ".join(words).title()
        if len(title) > 50:
            title = title[:47] + "..."
        
        # Generate summary based on text length
        if len(text) < 50:
            summary = f"This text discusses {title.lower()} and provides brief information on the topic."
        elif len(text) < 200:
            summary = f"The content covers {title.lower()} and explores key aspects of the subject matter."
        else:
            summary = f"This comprehensive text about {title.lower()} provides detailed insights and analysis on the topic."
        
        # Select random topics
        topics = random.choice(self.sample_topics)
        
        # Determine sentiment based on keywords
        text_lower = text.lower()
        sentiment = "neutral"
        
        positive_count = sum(1 for word in self.sentiment_keywords["positive"] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_keywords["negative"] if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        
        return {
            "summary": summary,
            "title": title,
            "topics": topics,
            "sentiment": sentiment
        }


class LLMAnalyzer:
    def __init__(self):
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your_openai_api_key_here':
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.")
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using OpenAI API to extract summary and structured metadata
        """
        try:
            # Generate summary and structured data
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a text analysis assistant. For the given text, provide:
                        1. A 1-2 sentence summary
                        2. A title (if available, otherwise "Untitled")
                        3. 3 key topics
                        4. Sentiment analysis (positive/neutral/negative)
                        
                        Return your response as a JSON object with these exact keys:
                        {
                            "summary": "1-2 sentence summary",
                            "title": "title or null",
                            "topics": ["topic1", "topic2", "topic3"],
                            "sentiment": "positive/neutral/negative"
                        }"""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                result = {
                    "summary": content,
                    "title": None,
                    "topics": ["general"],
                    "sentiment": "neutral"
                }
            
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class KeywordExtractor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def extract_keywords(self, text: str, num_keywords: int = 3) -> List[str]:
        """
        Extract the most frequent nouns from text
        """
        try:
            # Tokenize and tag words
            tokens = word_tokenize(text.lower())
            tagged_tokens = pos_tag(tokens)
            
            # Filter for nouns (NN, NNS, NNP, NNPS)
            nouns = [
                word for word, pos in tagged_tokens 
                if pos.startswith('NN') and 
                word.isalpha() and 
                len(word) > 2 and 
                word not in self.stop_words
            ]
            
            # Count frequency and return top N
            noun_counts = Counter(nouns)
            top_nouns = [word for word, count in noun_counts.most_common(num_keywords)]
            
            return top_nouns
            
        except Exception as e:
            # Fallback: return simple word frequency
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            words = [word for word in words if word not in self.stop_words]
            word_counts = Counter(words)
            return [word for word, count in word_counts.most_common(num_keywords)]


def calculate_confidence_score(text: str, llm_result: Dict[str, Any], keywords: List[str]) -> float:
    """
    Calculate a naive confidence score based on various factors
    """
    score = 0.0
    
    # Base score for having content
    if text and len(text.strip()) > 10:
        score += 0.2
    
    # Score for text length (longer texts often have more context)
    text_length = len(text.strip())
    if text_length > 100:
        score += 0.1
    if text_length > 500:
        score += 0.1
    
    # Score for having a good summary
    summary = llm_result.get("summary", "")
    if summary and len(summary.strip()) > 20:
        score += 0.2
    
    # Score for having a title
    if llm_result.get("title"):
        score += 0.1
    
    # Score for having topics
    topics = llm_result.get("topics", [])
    if len(topics) >= 3:
        score += 0.1
    elif len(topics) >= 2:
        score += 0.05
    
    # Score for having keywords
    if len(keywords) >= 3:
        score += 0.1
    elif len(keywords) >= 2:
        score += 0.05
    
    # Score for sentiment confidence (non-neutral sentiment is more confident)
    sentiment = llm_result.get("sentiment", "neutral")
    if sentiment != "neutral":
        score += 0.1
    
    # Ensure score is between 0.0 and 1.0
    return min(max(score, 0.0), 1.0)


def analyze_text_complete(text: str) -> Dict[str, Any]:
    """
    Complete text analysis combining LLM analysis and keyword extraction
    Falls back to mock analyzer if OpenAI is unavailable
    """
    if not text or not text.strip():
        raise ValueError("Empty input text")
    
    # Initialize keyword extractor (always works)
    keyword_extractor = KeywordExtractor()
    
    # Try OpenAI first, fallback to mock analyzer
    try:
        llm_analyzer = LLMAnalyzer()
        llm_result = llm_analyzer.analyze_text(text)
        analysis_method = "openai"
    except (ValueError, Exception) as e:
        # Fallback to mock analyzer
        print(f"OpenAI unavailable ({str(e)}), using mock analyzer")
        llm_analyzer = MockAnalyzer()
        llm_result = llm_analyzer.analyze_text(text)
        analysis_method = "mock"
    
    # Extract keywords
    keywords = keyword_extractor.extract_keywords(text)
    
    # Calculate confidence score
    confidence_score = calculate_confidence_score(text, llm_result, keywords)
    
    # Adjust confidence score for mock analysis (lower confidence)
    if analysis_method == "mock":
        confidence_score = min(confidence_score * 0.7, 0.8)  # Cap at 0.8 for mock
    
    # Combine results
    result = {
        "summary": llm_result.get("summary", ""),
        "title": llm_result.get("title"),
        "topics": llm_result.get("topics", []),
        "sentiment": llm_result.get("sentiment", "neutral"),
        "keywords": keywords,
        "confidence_score": confidence_score,
        "analysis_method": analysis_method  # Add method indicator
    }
    
    return result
