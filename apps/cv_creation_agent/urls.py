from django.urls import path
from . import views

app_name = 'cv_creation_agent'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('recommend-roles/', views.recommend_roles, name='recommend_roles'),
    path('skill-insights/', views.get_skill_insights, name='skill_insights'),
    path('available-roles/', views.get_available_roles, name='available_roles'),
    path('extract-skills/', views.extract_skills_from_text, name='extract_skills'),
]
