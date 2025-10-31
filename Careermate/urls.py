from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from apps.roadmap_agent.views import TestView


urlpatterns = [
    path('swagger/api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('swagger/api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/cv/', include('apps.cv_analysis_agent.urls')),
    path('api/v1/jobs/', include('apps.recommendation_agent.urls')),
    path('api/test/', TestView.as_view(), name='test'),
]
