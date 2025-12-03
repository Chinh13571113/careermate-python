from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .core.recommender import create_recommender
from .core.nlp_extractor import create_skill_extractor
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .swagger_schemas import (
    RecommendRolesRequestSerializer,
    ExtractSkillsRequestSerializer,
    SkillInsightsRequestSerializer,
    RecommendRolesResponseSerializer,
    ExtractSkillsResponseSerializer,
    SkillInsightsResponseSerializer,
    AvailableRolesResponseSerializer,
    HealthCheckResponseSerializer
)

# Set up logging
logger = logging.getLogger(__name__)

recommender = None
skill_extractor = None
try:
    recommender = create_recommender()
    skill_extractor = create_skill_extractor(recommender)
    print("Career Recommender and Skill Extractor initialized")
except Exception as e:
    print(f"Failed to initialize recommender: {e}")

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="Recommend career roles based on skills and experience. Accepts BOTH structured input (skills array) OR free-form text.",
    request_body=RecommendRolesRequestSerializer,
    responses={
        200: RecommendRolesResponseSerializer,
        400: "No skills or text provided",
        500: "Server error"
    }
)
def recommend_roles(request):
    """
    Recommend career roles based on skills and experience
    
    Accepts BOTH input formats:
    1. Structured: {"skills": [...], "experience_years": N}
    2. Free-form: {"text": "I have 5 years experience with Python..."}
    """
    logger.info(f"🔵 recommend_roles called - Method: {request.method}, Origin: {request.META.get('HTTP_ORIGIN', 'N/A')}")
    logger.info(f"🔵 Headers: {dict(request.headers)}")
    
    if not recommender:
        logger.error("❌ Recommender not initialized")
        return JsonResponse({'success': False, 'error': 'Recommender not initialized'}, status=500)

    try:
        # Check if request body is empty
        if not request.body:
            logger.error("❌ Empty request body")
            return JsonResponse({
                'success': False,
                'error': 'Request body is empty. Please provide either "skills" array or "text" field.'
            }, status=400)

        # Try to parse JSON
        try:
            data = json.loads(request.body)
            logger.info(f"✅ Request body parsed: {data}")
        except json.JSONDecodeError as json_err:
            logger.error(f"❌ Invalid JSON: {str(json_err)}")
            logger.error(f"❌ Request body (first 200 chars): {request.body[:200]}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON format. Please send valid JSON with either "skills" array or "text" field.',
                'details': str(json_err)
            }, status=400)

        # Check if free-form text input
        if 'text' in data:
            if not skill_extractor:
                return JsonResponse({'success': False, 'error': 'Skill extractor not initialized'}, status=500)
            
            text = data.get('text', '')
            if not text or not text.strip():
                return JsonResponse({'success': False, 'error': 'Text input is empty'}, status=400)
            
            # Extract skills and experience from text
            extraction_result = skill_extractor.get_extraction_confidence(text)
            parsed = extraction_result['parsed_data']
            confidence_metrics = extraction_result['confidence_metrics']
            
            skills = parsed['skills']
            experience_years = parsed['experience_years']
            
            if not skills:
                return JsonResponse({
                    'success': False,
                    'error': 'Could not extract any skills from text',
                    'suggestion': 'Please mention specific technologies, frameworks, or programming languages',
                    'confidence_metrics': confidence_metrics
                }, status=400)
            
            # Get recommendations
            recommendations = recommender.recommend_roles(skills=skills, experience_years=experience_years, top_n=5)
            insights = recommender.get_skill_insights(skills)
            
            return JsonResponse({
                'success': True,
                'input_type': 'free_text',
                'extracted_skills': skills,
                'extracted_experience': experience_years,
                'confidence_metrics': confidence_metrics,
                'recommendations': recommendations,
                'total_skills': len(skills),
                'skill_insights': insights
            })
        
        # Structured input (original format)
        else:
            skills = data.get('skills', [])
            experience_years = float(data.get('experience_years', 0))
            
            if not skills:
                return JsonResponse({'success': False, 'error': 'Skills are required'}, status=400)
            
            recommendations = recommender.recommend_roles(skills=skills, experience_years=experience_years, top_n=5)
            insights = recommender.get_skill_insights(skills)
            
            return JsonResponse({
                'success': True,
                'input_type': 'structured',
                'recommendations': recommendations,
                'total_skills': len(skills),
                'skill_insights': insights
            })
            
    except Exception as e:
        logger.error(f"❌ Error in recommend_roles: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="Get insights about specific skills - which roles use them, how common they are, etc.",
    request_body=SkillInsightsRequestSerializer,
    responses={
        200: SkillInsightsResponseSerializer,
        400: "Skills are required",
        500: "Server error"
    }
)
def get_skill_insights(request):
    if not recommender:
        return JsonResponse({'success': False, 'error': 'Recommender not initialized'}, status=500)
    try:
        data = json.loads(request.body)
        skills = data.get('skills', [])
        if not skills:
            return JsonResponse({'success': False, 'error': 'Skills are required'}, status=400)
        insights = recommender.get_skill_insights(skills)
        return JsonResponse({'success': True, 'insights': insights})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="List all 12 available career roles with their requirements",
    manual_parameters=[],
    responses={
        200: AvailableRolesResponseSerializer,
        500: "Server error"
    }
)
def get_available_roles(request):
    if not recommender:
        return JsonResponse({'success': False, 'error': 'Recommender not initialized'}, status=500)
    try:
        roles_info = []
        for role_name, requirements in recommender.ROLE_PATTERNS.items():
            roles_info.append({'role': role_name, 'required_languages': requirements['languages'][:5], 'common_technologies': requirements['technologies'][:10], 'keywords': requirements['keywords']})
        return JsonResponse({'success': True, 'total_roles': len(roles_info), 'roles': roles_info})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="Health check endpoint to verify API status",
    manual_parameters=[],
    responses={
        200: HealthCheckResponseSerializer
    }
)
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'recommender_initialized': recommender is not None
    })

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="Extract skills and experience from free-form text using NLP",
    request_body=ExtractSkillsRequestSerializer,
    responses={
        200: ExtractSkillsResponseSerializer,
        400: "No text provided",
        500: "Server error"
    }
)
def extract_skills_from_text(request):
    """Extract skills and experience from free-form text using NLP"""
    if not skill_extractor:
        return JsonResponse({
            'success': False,
            'error': 'Skill extractor not initialized'
        }, status=500)
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text is required'
            }, status=400)
        
        # Use NLP extractor to parse the text
        skills = skill_extractor.extract_skills(text)
        experience_years = skill_extractor.extract_experience(text)
        
        return JsonResponse({
            'success': True,
            'extracted_data': {
                'skills': skills,
                'experience_years': experience_years,
                'raw_text': text
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
