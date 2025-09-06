from django.db import models
import json


class TextAnalysis(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    
    # Original text input
    original_text = models.TextField()
    
    # Generated summary
    summary = models.TextField()
    
    # Structured metadata
    title = models.CharField(max_length=500, blank=True, null=True)
    topics = models.JSONField(default=list)  # List of 3 key topics
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    keywords = models.JSONField(default=list)  # List of 3 most frequent nouns
    confidence_score = models.FloatField(default=0.0, help_text="Confidence score from 0.0 to 1.0")
    analysis_method = models.CharField(max_length=10, default='openai', help_text="Method used for analysis (openai/mock)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis {self.id}: {self.title or 'Untitled'}"
    
    def to_dict(self):
        """Convert model instance to dictionary for API responses"""
        return {
            'id': self.id,
            'original_text': self.original_text,
            'summary': self.summary,
            'title': self.title,
            'topics': self.topics,
            'sentiment': self.sentiment,
            'keywords': self.keywords,
            'confidence_score': self.confidence_score,
            'analysis_method': self.analysis_method,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }