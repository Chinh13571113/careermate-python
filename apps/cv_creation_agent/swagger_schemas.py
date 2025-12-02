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


# Response Serializers
class RecommendationSerializer(serializers.Serializer):
    """Schema for a single recommendation"""
    role = serializers.CharField()
    confidence = serializers.FloatField()
    match_score = serializers.FloatField()
    matched_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())
    insights = serializers.CharField()


class RecommendRolesResponseSerializer(serializers.Serializer):
    """Response schema for recommend_roles endpoint"""
    success = serializers.BooleanField()
    input_type = serializers.CharField(required=False)
    extracted_skills = serializers.ListField(child=serializers.CharField(), required=False)
    extracted_experience = serializers.IntegerField(required=False)
    recommendations = RecommendationSerializer(many=True)
    total_skills = serializers.IntegerField()
    skill_insights = serializers.DictField(required=False)


class ExtractedDataSerializer(serializers.Serializer):
    """Schema for extracted data"""
    skills = serializers.ListField(child=serializers.CharField())
    experience_years = serializers.IntegerField()
    raw_text = serializers.CharField()


class ExtractSkillsResponseSerializer(serializers.Serializer):
    """Response schema for extract_skills endpoint"""
    success = serializers.BooleanField()
    extracted_data = ExtractedDataSerializer()


class SkillInsightsResponseSerializer(serializers.Serializer):
    """Response schema for skill_insights endpoint"""
    success = serializers.BooleanField()
    insights = serializers.DictField()


class RoleInfoSerializer(serializers.Serializer):
    """Schema for role information"""
    role = serializers.CharField()
    required_languages = serializers.ListField(child=serializers.CharField())
    common_technologies = serializers.ListField(child=serializers.CharField())
    keywords = serializers.ListField(child=serializers.CharField())


class AvailableRolesResponseSerializer(serializers.Serializer):
    """Response schema for get_available_roles endpoint"""
    success = serializers.BooleanField()
    total_roles = serializers.IntegerField()
    roles = RoleInfoSerializer(many=True)


class HealthCheckResponseSerializer(serializers.Serializer):
    """Response schema for health_check endpoint"""
    status = serializers.CharField()
    recommender_initialized = serializers.BooleanField()
