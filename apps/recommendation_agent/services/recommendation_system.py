"""
Recommendation System - Main orchestrator for job recommendations

This module provides a unified interface for different recommendation strategies:
- Content-Based: Semantic similarity with skill overlap
- Collaborative Filtering: User-based recommendations
- Hybrid: Combined approach
"""
import os
import sys
import django
from sqlalchemy import create_engine

# Setup Django environment
django_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(django_base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

from django.conf import settings

# Import recommendation services
from apps.recommendation_agent.services.content_based_recommender import get_content_based_recommendations
from apps.recommendation_agent.services.collaborative_recommender import get_collaborative_filtering_recommendations
from apps.recommendation_agent.services.hybrid_recommender import get_hybrid_job_recommendations
from apps.recommendation_agent.services.job_query_service import query_all_jobs, query_all_jobs_async
from apps.recommendation_agent.services.embedding_service import get_gemini_embedding


def get_sqlalchemy_engine():
    """
    Create SQLAlchemy engine from Django database settings

    Returns:
        Engine: SQLAlchemy database engine
    """
    db_settings = settings.DATABASES['default']
    engine = db_settings.get('ENGINE', '')

    if 'postgresql' in engine:
        db_url = f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings.get('PORT', 5432)}/{db_settings['NAME']}"
    elif 'mysql' in engine:
        db_url = f"mysql+pymysql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings.get('PORT', 3306)}/{db_settings['NAME']}"
    else:
        # SQLite or other
        db_url = f"sqlite:///{db_settings['NAME']}"

    return create_engine(db_url)


# Re-export main functions for backward compatibility
__all__ = [
    'get_content_based_recommendations',
    'get_collaborative_filtering_recommendations',
    'get_hybrid_job_recommendations',
    'query_all_jobs',
    'query_all_jobs_async',
    'get_gemini_embedding',
    'get_sqlalchemy_engine'
]
