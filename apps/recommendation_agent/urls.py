from django.urls import path
from .views import (
    RecommendJobView,
    FeedbackView,
    SyncJobFromPostgresView,
    GetJobRecommendationsView,
    CleanupWeaviateView,
    DeleteJobFromWeaviateView,
    TrainCFModelView,
    CFModelStatsView,
    PureCFRecommendationsView,
    UserCFEmbeddingView,
    JobCFEmbeddingView
)

urlpatterns = [
    # Job sync and management
    path("sync/", SyncJobFromPostgresView.as_view(), name="sync-jobs"),
    path("cleanup/", CleanupWeaviateView.as_view(), name="cleanup-weaviate"),
    path("weaviate/<int:job_id>/", DeleteJobFromWeaviateView.as_view(), name="delete-job-weaviate"),

    # Job recommendations (hybrid: content-based + collaborative filtering)
    path("recommendations/", GetJobRecommendationsView.as_view(), name="get-recommendations"),
    path("recommend/", RecommendJobView.as_view(), name="recommend-jobs"),

    # Feedback collection
    path("feedback/", FeedbackView.as_view(), name="job-feedback"),

    # Collaborative Filtering endpoints
    path("cf/train/", TrainCFModelView.as_view(), name="train-cf-model"),
    path("cf/stats/", CFModelStatsView.as_view(), name="cf-model-stats"),
    path("cf/recommendations/", PureCFRecommendationsView.as_view(), name="pure-cf-recommendations"),
    path("cf/users/<int:candidate_id>/embedding/", UserCFEmbeddingView.as_view(), name="user-cf-embedding"),
    path("cf/jobs/<int:job_id>/embedding/", JobCFEmbeddingView.as_view(), name="job-cf-embedding"),
]
