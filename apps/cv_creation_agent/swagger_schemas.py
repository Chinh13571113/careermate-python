"""
Serializers for Swagger API documentation
These help Swagger UI display proper request/response schemas
"""
from rest_framework import serializers


class RecommendRolesRequestSerializer(serializers.Serializer):
    """Request schema for recommend_roles endpoint"""
    text = serializers.CharField(
        required=False,
        help_text='Free-form text describing your experience (e.g., "I have 5 years experience with Python, Django, and React")',
        style={'base_template': 'textarea.html'}
    )
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='List of skills (use this OR text, not both)'
    )
    experience_years = serializers.IntegerField(
        required=False,
        help_text='Years of experience (optional, will be extracted from text if provided there)'
    )


class ExtractSkillsRequestSerializer(serializers.Serializer):
    """Request schema for extract_skills endpoint"""
    text = serializers.CharField(
        required=True,
        help_text='Free-form text describing your experience, skills, and background',
        style={'base_template': 'textarea.html'}
    )


class SkillInsightsRequestSerializer(serializers.Serializer):
    """Request schema for skill_insights endpoint"""
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text='List of skills to analyze'
    )
