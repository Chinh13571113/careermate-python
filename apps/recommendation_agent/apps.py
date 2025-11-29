from django.apps import AppConfig


class RecommendationAgentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.recommendation_agent"

    def ready(self):
        """Import signals when Django starts"""