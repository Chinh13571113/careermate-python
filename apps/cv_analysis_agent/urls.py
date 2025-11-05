# apps/cv_creation_agent/urls.py
from django.urls import path
from .view.resume_parser_view import CVAnalyzeView, CVTaskStatusView, CVAnalyzeSyncView
from .view.resume_analysis_view import ResumeAtsAnalyzeView

urlpatterns = [
    path("analyze_cv/", CVAnalyzeView.as_view(), name="analyze_cv"),
    path("task-status/<str:task_id>/", CVTaskStatusView.as_view(), name="task_status"),
    path("analyze-ats/", ResumeAtsAnalyzeView.as_view(), name="resume-analyze-ats"),
]
