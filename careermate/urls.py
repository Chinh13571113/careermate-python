from django.urls import path, include

from apps.roadmap_agent.views import TestView
from home.swagger import schema_view

urlpatterns = [
    path('api/v1/', include('apps.cv_analysis_agent.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/test/', TestView.as_view(), name='test'),
]
