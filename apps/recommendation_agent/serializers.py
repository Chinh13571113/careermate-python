from rest_framework import serializers

class IndexJobSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    title = serializers.CharField(allow_blank=True)
    skills = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    description = serializers.CharField(allow_blank=True)

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
