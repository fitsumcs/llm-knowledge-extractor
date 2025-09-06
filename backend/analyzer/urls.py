from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_text, name='analyze_text'),
    path('batch-analyze/', views.batch_analyze_texts, name='batch_analyze_texts'),
    path('search/', views.search_analyses, name='search_analyses'),
    path('list/', views.list_analyses, name='list_analyses'),
    path('<int:analysis_id>/', views.get_analysis, name='get_analysis'),
]
