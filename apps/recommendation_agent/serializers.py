from rest_framework import serializers

from apps.recommendation_agent.models import Resume, Skill, Candidate


class IndexJobSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    title = serializers.CharField(allow_blank=True)
    skills = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    description = serializers.CharField(allow_blank=True)

class JobPostingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    address = serializers.CharField(allow_blank=True)
    status = serializers.CharField(allow_blank=True)
    expiration_date = serializers.DateField(allow_null=True)
    created_at = serializers.DateField(allow_null=True)
    recruiter_id = serializers.IntegerField()
    company_name = serializers.CharField(allow_blank=True)
    skills = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)

class AccountSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField(allow_blank=True)
    status = serializers.CharField(allow_blank=True)

class RecommendSerializer(serializers.Serializer):
    cv_text = serializers.CharField(allow_blank=True, required=False)
    candidate_id = serializers.IntegerField(required=False)
    query_text = serializers.CharField(required=False, allow_blank=True)
    top_k = serializers.IntegerField(default=10)
    alpha = serializers.FloatField(default=0.7)  # Balance between vector (1.0) and keyword (0.0) search
    x = serializers.FloatField(default=0.7)  # CB weight (1-x = CF weight)

class FeedbackSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    job_id = serializers.IntegerField()
    feedback_type = serializers.ChoiceField(choices=["like", "dislike", "save", "apply"])
    score = serializers.FloatField(required=False, default=1.0)

class TrainCFModelSerializer(serializers.Serializer):
    embedding_size = serializers.IntegerField(default=64, help_text="Embedding dimension (latent factors)")
    learning_rate = serializers.FloatField(default=0.001, help_text="Learning rate for training")
    epochs = serializers.IntegerField(default=30, help_text="Number of training epochs")
    model_type = serializers.ChoiceField(
        choices=["BPR"],
        default="BPR",
        help_text="Model type: 'BPR' (Bayesian Personalized Ranking - recommended for implicit feedback)"
    )

class JobRecommendationRequestSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField(required=True, help_text="ID of the candidate to get recommendations for")
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of skills to match (e.g., ['Python', 'Django', 'PostgreSQL'])"
    )
    title = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Job title or candidate title to match (e.g., 'Backend Developer')"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Job description or candidate profile description to match"
    )
    top_n = serializers.IntegerField(required=False, default=5, help_text="Number of top recommendations to return")

class JobRecommendationResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField()
    candidate_id = serializers.IntegerField()
    results = serializers.ListField(child=serializers.DictField())

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skillID', 'skill_type', 'skill_name', 'yearOfExperience']


class ResumeSerializer(serializers.ModelSerializer):
    # nested list skill
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = ['resumeID', 'about_me', 'createAt', 'skills']


class CandidateSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    title = serializers.CharField(allow_blank=True, allow_null=True)
    fullname = serializers.CharField(allow_blank=True, allow_null=True)
    email = serializers.EmailField()
    skills = serializers.ListField(child=serializers.DictField(), allow_empty=True)
