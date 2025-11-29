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
from .swagger_schemas import (
    RecommendRolesRequestSerializer,
    ExtractSkillsRequestSerializer,
    SkillInsightsRequestSerializer
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
    request_body=RecommendRolesRequestSerializer,
    responses={
        200: openapi.Response(
            description="Recommendations returned successfully",
            examples={
                "application/json": {
                    "success": True,
                    "recommendations": [
                        {
                            "role": "Backend Developer",
                            "confidence": 95.5,
                            "match_score": 0.88,
                            "matched_skills": ["Python", "Django", "PostgreSQL"],
                            "missing_skills": ["Java"],
                            "insights": "Strong backend focus with database expertise"
                        }
                    ],
                    "input_summary": {
                        "total_skills": 7,
                        "experience_years": 5
                    }
                }
            }
        ),
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
        data = json.loads(request.body)
        logger.info(f"✅ Request body parsed: {data}")
        
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
    request_body=SkillInsightsRequestSerializer,
    responses={200: "Skill insights returned successfully"}
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
    responses={
        200: openapi.Response(
            description="List of all available roles",
            examples={
                "application/json": {
                    "success": True,
                    "total_roles": 12,
                    "roles": [
                        {
                            "role": "Backend Developer",
                            "required_languages": ["Python", "Java", "C#"],
                            "common_technologies": ["Django", "Flask", "Spring"],
                            "keywords": ["backend", "server", "api"]
                        }
                    ]
                }
            }
        )
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
    responses={
        200: openapi.Response(
            description="API is healthy",
            examples={
                "application/json": {
                    "status": "healthy",
                    "recommender_initialized": True
                }
            }
        )
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
    request_body=ExtractSkillsRequestSerializer,
    responses={
        200: openapi.Response(
            description="Skills extracted successfully",
            examples={
                "application/json": {
                    "success": True,
                    "extracted_data": {
                        "skills": ["Python", "Django", "React", "PostgreSQL", "Docker", "REST API", "AWS"],
                        "experience_years": 5,
                        "raw_text": "I've been working as a software developer..."
                    }
                }
            }
        ),
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
