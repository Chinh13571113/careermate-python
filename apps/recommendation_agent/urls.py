from django.urls import path
from .views import JobPostingView


urlpatterns = [
    # Get all Job Postings
    path('job-postings/', JobPostingView.as_view(), name='get_job_postings'),

]
