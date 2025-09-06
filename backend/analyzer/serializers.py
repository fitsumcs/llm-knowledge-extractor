from rest_framework import serializers
from .models import TextAnalysis


class TextAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnalysis
        fields = ['id', 'original_text', 'summary', 'title', 'topics', 'sentiment', 'keywords', 'confidence_score', 'analysis_method', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnalyzeTextSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=10000, help_text="Text to analyze")
    
    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Text cannot be empty")
        return value.strip()


class SearchSerializer(serializers.Serializer):
    topic = serializers.CharField(required=False, help_text="Topic to search for")
    keyword = serializers.CharField(required=False, help_text="Keyword to search for")
    sentiment = serializers.ChoiceField(choices=['positive', 'neutral', 'negative'], required=False, help_text="Sentiment to filter by")
    
    def validate(self, data):
        if not any(data.values()):
            raise serializers.ValidationError("At least one search parameter must be provided")
        return data


class BatchAnalyzeSerializer(serializers.Serializer):
    texts = serializers.ListField(
        child=serializers.CharField(max_length=10000),
        min_length=1,
        max_length=10,
        help_text="List of texts to analyze (max 10 texts)"
    )
    
    def validate_texts(self, value):
        if not value:
            raise serializers.ValidationError("At least one text must be provided")
        
        for text in value:
            if not text or not text.strip():
                raise serializers.ValidationError("All texts must be non-empty")
        
        return value
