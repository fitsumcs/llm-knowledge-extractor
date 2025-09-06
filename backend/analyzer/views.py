from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import TextAnalysis
from .serializers import TextAnalysisSerializer, AnalyzeTextSerializer, SearchSerializer, BatchAnalyzeSerializer
from .utils import analyze_text_complete
import logging

logger = logging.getLogger(__name__)


@extend_schema(
    operation_id='analyze_text',
    summary='Analyze text using AI',
    description='Analyze unstructured text using OpenAI GPT to extract summary, topics, sentiment, and keywords.',
    request=AnalyzeTextSerializer,
    responses={
        201: TextAnalysisSerializer,
        400: {'description': 'Bad request - Invalid input or empty text'},
        500: {'description': 'Internal server error - AI analysis failed'}
    },
    examples=[
        OpenApiExample(
            'Example Request',
            summary='Analyze a sample text',
            description='Example of analyzing a text about technology',
            value={
                'text': 'Artificial intelligence is transforming the way we work and live. Machine learning algorithms are becoming more sophisticated and are being applied to various industries including healthcare, finance, and transportation.'
            }
        )
    ]
)
@api_view(['POST'])
def analyze_text(request):
    """
    Analyze text using LLM and return structured data
    """
    serializer = AnalyzeTextSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    text = serializer.validated_data['text']
    
    try:
        # Analyze the text
        analysis_result = analyze_text_complete(text)
        
        # Create and save the analysis
        analysis = TextAnalysis.objects.create(
            original_text=text,
            summary=analysis_result['summary'],
            title=analysis_result['title'],
            topics=analysis_result['topics'],
            sentiment=analysis_result['sentiment'],
            keywords=analysis_result['keywords'],
            confidence_score=analysis_result['confidence_score'],
            analysis_method=analysis_result['analysis_method']
        )
        
        # Return the result
        response_serializer = TextAnalysisSerializer(analysis)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        return Response(
            {'error': 'Failed to analyze text. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id='search_analyses',
    summary='Search analyses',
    description='Search through stored text analyses by topic, keyword, or sentiment.',
    parameters=[
        OpenApiParameter(
            name='topic',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search by topic (e.g., "technology", "health")',
            required=False
        ),
        OpenApiParameter(
            name='keyword',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search by keyword (e.g., "AI", "climate")',
            required=False
        ),
        OpenApiParameter(
            name='sentiment',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by sentiment',
            enum=['positive', 'neutral', 'negative'],
            required=False
        )
    ],
    responses={
        200: TextAnalysisSerializer(many=True),
        400: {'description': 'Bad request - No search parameters provided'}
    },
    examples=[
        OpenApiExample(
            'Search by topic',
            summary='Search for technology-related analyses',
            description='Find all analyses related to technology',
            value={'topic': 'technology'}
        ),
        OpenApiExample(
            'Search by sentiment',
            summary='Find positive analyses',
            description='Get all analyses with positive sentiment',
            value={'sentiment': 'positive'}
        )
    ]
)
@api_view(['GET'])
def search_analyses(request):
    """
    Search stored analyses by topic, keyword, or sentiment
    """
    serializer = SearchSerializer(data=request.query_params)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    topic = serializer.validated_data.get('topic')
    keyword = serializer.validated_data.get('keyword')
    sentiment = serializer.validated_data.get('sentiment')
    
    # Build query
    query = Q()
    
    if topic:
        query |= Q(topics__icontains=topic)
    
    if keyword:
        query |= Q(keywords__icontains=keyword) | Q(original_text__icontains=keyword)
    
    if sentiment:
        query &= Q(sentiment=sentiment)
    
    # Execute query
    analyses = TextAnalysis.objects.filter(query).order_by('-created_at')
    
    # Serialize and return
    response_serializer = TextAnalysisSerializer(analyses, many=True)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='list_analyses',
    summary='List all analyses',
    description='Retrieve all stored text analyses with pagination.',
    responses={
        200: TextAnalysisSerializer(many=True)
    }
)
@api_view(['GET'])
def list_analyses(request):
    """
    List all stored analyses
    """
    analyses = TextAnalysis.objects.all().order_by('-created_at')
    serializer = TextAnalysisSerializer(analyses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='get_analysis',
    summary='Get analysis by ID',
    description='Retrieve a specific text analysis by its ID.',
    responses={
        200: TextAnalysisSerializer,
        404: {'description': 'Analysis not found'}
    }
)
@api_view(['GET'])
def get_analysis(request, analysis_id):
    """
    Get a specific analysis by ID
    """
    try:
        analysis = TextAnalysis.objects.get(id=analysis_id)
        serializer = TextAnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TextAnalysis.DoesNotExist:
        return Response(
            {'error': 'Analysis not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id='batch_analyze_texts',
    summary='Batch analyze multiple texts',
    description='Analyze multiple texts at once using AI to extract summaries, topics, sentiment, and keywords for each.',
    request=BatchAnalyzeSerializer,
    responses={
        201: TextAnalysisSerializer(many=True),
        400: {'description': 'Bad request - Invalid input or empty texts'},
        500: {'description': 'Internal server error - AI analysis failed'}
    },
    examples=[
        OpenApiExample(
            'Example Request',
            summary='Analyze multiple texts',
            description='Example of analyzing multiple texts about different topics',
            value={
                'texts': [
                    'Artificial intelligence is transforming healthcare with new diagnostic tools.',
                    'Climate change requires immediate action from governments worldwide.',
                    'The new smartphone features advanced camera technology and longer battery life.'
                ]
            }
        )
    ]
)
@api_view(['POST'])
def batch_analyze_texts(request):
    """
    Analyze multiple texts using LLM and return structured data for each
    """
    serializer = BatchAnalyzeSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    texts = serializer.validated_data['texts']
    analyses = []
    errors = []
    
    for i, text in enumerate(texts):
        try:
            # Analyze the text
            analysis_result = analyze_text_complete(text)
            
            # Create and save the analysis
            analysis = TextAnalysis.objects.create(
                original_text=text,
                summary=analysis_result['summary'],
                title=analysis_result['title'],
                topics=analysis_result['topics'],
                sentiment=analysis_result['sentiment'],
                keywords=analysis_result['keywords'],
                confidence_score=analysis_result['confidence_score'],
                analysis_method=analysis_result['analysis_method']
            )
            
            analyses.append(analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing text {i+1}: {str(e)}")
            errors.append({
                'index': i,
                'text': text[:100] + '...' if len(text) > 100 else text,
                'error': str(e)
            })
    
    # Serialize successful analyses
    response_serializer = TextAnalysisSerializer(analyses, many=True)
    
    response_data = {
        'analyses': response_serializer.data,
        'total_processed': len(analyses),
        'total_requested': len(texts),
        'success_count': len(analyses),
        'error_count': len(errors)
    }
    
    if errors:
        response_data['errors'] = errors
    
    return Response(response_data, status=status.HTTP_201_CREATED)