import base64
import os

from celery.result import AsyncResult
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from Careermate import celery_app
from ..services.analyzer_service import analyze_resume_sync
from ..serializers import ResumeUploadSerializer
from ..task import process_resume_task
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

TMP_DIR = "/tmp/uploads"
os.makedirs(TMP_DIR, exist_ok=True)

@extend_schema(
    tags=["CV Parser"],
    summary="Analyze CV/Resume (Async)",
    description="Upload a CV/Resume file for asynchronous analysis. Returns a task_id to check status later.",
    request=ResumeUploadSerializer,
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
        400: OpenApiResponse(
            description="Invalid request data",
            examples=[
                OpenApiExample(
                    "Missing file",
                    value={
                        "file": ["This field is required."]
                    }
                )
            ]
        )
    }
)
class CVAnalyzeView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ResumeUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']

        # Read file content and encode to base64
        file_content = file.read()
        file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        filename = file.name

        task = process_resume_task.delay(file_content_b64, filename)
        return Response({
            "task_id": task.id,
            "status": "processing"
        }, status=status.HTTP_202_ACCEPTED)

@extend_schema(
    tags=["CV Parser"],
    summary="Get CV Analysis Task Status",
    description="Check the status and result of a CV analysis task using task_id.",
    responses={
        200: OpenApiResponse(
            response={"type": "object"},
            description="Task completed successfully",
            examples=[
                OpenApiExample(
                    "Completed",
                    value={
                        "status": "completed",
                        "data": {
                            "personal_info": {
                                "name": "John Doe",
                                "email": "john.doe@example.com",
                                "phone": "+1234567890",
                                "address": "New York, USA"
                            },
                            "education": [
                                {
                                    "degree": "Bachelor of Science",
                                    "field": "Computer Science",
                                    "institution": "ABC University",
                                    "year": "2020"
                                }
                            ],
                            "experience": [
                                {
                                    "title": "Software Engineer",
                                    "company": "Tech Corp",
                                    "duration": "2020-2023",
                                    "description": "Developed web applications"
                                }
                            ],
                            "skills": ["Python", "Django", "PostgreSQL", "Docker"],
                            "certifications": ["AWS Certified Developer"],
                            "feedback": {
                                "strengths": ["Strong technical background", "Clear presentation"],
                                "improvements": ["Add more quantifiable achievements"],
                                "overall_score": 8.5
                            }
                        }
                    }
                )
            ]
        ),
        202: OpenApiResponse(
            description="Task still processing",
            examples=[
                OpenApiExample(
                    "Pending",
                    value={"status": "pending"}
                ),
                OpenApiExample(
                    "In Progress",
                    value={"status": "in_progress"}
                )
            ]
        ),
        500: OpenApiResponse(
            description="Task failed",
            examples=[
                OpenApiExample(
                    "Failed",
                    value={
                        "status": "failed",
                        "error": "Unable to parse PDF file"
                    }
                )
            ]
        )
    }
)
class CVTaskStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, task_id):
        result = AsyncResult(task_id, app=celery_app)
        if result.state == "SUCCESS":
            return Response({
                "status": "completed",
                "data": result.result
            }, status=status.HTTP_200_OK)
        elif result.state == "PENDING":
            return Response({"status": "pending"}, status=status.HTTP_202_ACCEPTED)
        elif result.state == "STARTED":
            return Response({"status": "in_progress"}, status=status.HTTP_202_ACCEPTED)
        elif result.state == "FAILURE":
            return Response({
                "status": "failed",
                "error": str(result.result)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"status": result.state}, status=status.HTTP_200_OK)



@extend_schema(
    tags=["CV Analysis"],
    summary="Analyze CV/Resume (Sync)",
    description="Upload a CV/Resume file for synchronous analysis. POST with feedback, PUT without feedback.",
    request=ResumeUploadSerializer,
    responses={
        200: OpenApiResponse(
            response={"type": "object"},
            description="CV analyzed successfully",
            examples=[
                OpenApiExample(
                    "Success with feedback",
                    value={
                        "personal_info": {
                            "name": "Jane Smith",
                            "email": "jane.smith@example.com",
                            "phone": "+9876543210",
                            "linkedin": "linkedin.com/in/janesmith"
                        },
                        "education": [
                            {
                                "degree": "Master of Science",
                                "field": "Data Science",
                                "institution": "XYZ University",
                                "year": "2022",
                                "gpa": "3.8/4.0"
                            }
                        ],
                        "experience": [
                            {
                                "title": "Data Analyst",
                                "company": "Data Corp",
                                "duration": "2022-Present",
                                "description": "Analyzed business metrics and created dashboards"
                            }
                        ],
                        "skills": ["Python", "SQL", "Tableau", "Machine Learning"],
                        "projects": [
                            {
                                "name": "Customer Churn Prediction",
                                "description": "Built ML model to predict customer churn"
                            }
                        ],
                        "feedback": {
                            "strengths": [
                                "Strong analytical skills",
                                "Relevant project experience",
                                "Good educational background"
                            ],
                            "improvements": [
                                "Add more quantified results",
                                "Include leadership experience"
                            ],
                            "overall_score": 7.8,
                            "recommendations": [
                                "Highlight impact of your projects with numbers",
                                "Add certifications in relevant tools"
                            ]
                        }
                    }
                ),
                OpenApiExample(
                    "Success without feedback",
                    value={
                        "personal_info": {
                            "name": "Bob Johnson",
                            "email": "bob@example.com"
                        },
                        "education": [],
                        "experience": [],
                        "skills": ["Java", "Spring Boot", "MySQL"]
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Invalid request",
            examples=[
                OpenApiExample(
                    "Invalid file type",
                    value={
                        "file": ["Invalid file format. Only PDF and DOCX are supported."]
                    }
                )
            ]
        ),
        500: OpenApiResponse(
            description="Analysis failed",
            examples=[
                OpenApiExample(
                    "Processing error",
                    value={
                        "error": "Failed to extract text from PDF"
                    }
                )
            ]
        )
    }
)
class CVAnalyzeSyncView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ResumeUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']

        try:
            result = analyze_resume_sync(file, True)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        serializer = ResumeUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        file = serializer.validated_data['file']
        try:
            result = analyze_resume_sync(file, False)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
