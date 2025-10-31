from django.urls import path
from .views import JobPostingView, AccountView, CandidateView


urlpatterns = [
    # Get all Job Postings
    path('job-postings/', JobPostingView.as_view(), name='get_job_postings'),
    # Get all Accounts
    path('accounts/', AccountView.as_view(), name='get_accounts'),
    # Get all Candidates with Skills
    path('candidates/', CandidateView.as_view(), name='get_candidates'),
]
