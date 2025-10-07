from django.urls import path, include
from django.contrib import admin
from apps.ai_career_path.views import RoadmapGenerateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/roadmap/generate/', RoadmapGenerateView.as_view()),
]
