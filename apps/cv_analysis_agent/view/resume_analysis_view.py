from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from ..serializers import ResumeAnalysisSerializer
from ..services import ai_checker_resume_service

@extend_schema(
    tags=["CV Analysis"],
    summary="Analyze CV/Resume (Async)",
    description="Upload a CV/Resume file and description for asynchronous analysis. Returns a task_id to check status "
                "later.",
    request=ResumeAnalysisSerializer,
    responses={
        202: OpenApiResponse(
            response={"type": "object"},
            description="Task created successfully",
            examples=[
                OpenApiExample(
                    "Success",
                    value={
                        "task_id": "a1b2c3d4-5678-90ef-ghij-klmnopqrstuv",
                        "status": "processing"
                    }
                )
            ]
        ),
    }
)
class ResumeAtsAnalyzeView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        s = ResumeAnalysisSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        jd = s.validated_data.get("job_description", "")
        cv = s.validated_data["cv_file"]
        result = ai_checker_resume_service.analyze_cv_vs_jd(cv, jd)
        return Response(result)
