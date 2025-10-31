from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from .models import JobPostings, JobDescription, Account, Candidate, Resume, Skill
from .serializers import JobPostingSerializer, AccountSerializer, CandidateSerializer


class JobPostingView(APIView):
    """
    API endpoint to get all job postings with filters
    GET /job-postings/ - List all job postings
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get list of job postings with optional filtering
        Query params:
        - status: Filter by status (e.g., 'ACTIVE')
        - recruiter_id: Filter by recruiter ID
        - limit: Number of results to return (default: 20)
        - offset: Offset for pagination (default: 0)
        """
        try:
            # Get query parameters
            job_status = request.GET.get('status', None)
            recruiter_id = request.GET.get('recruiter_id', None)
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))

            # Build query
            queryset = JobPostings.objects.select_related('recruiter').prefetch_related(
                Prefetch('jobdescription_set', queryset=JobDescription.objects.select_related('jd_skill'))
            )

            # Apply filters
            if job_status:
                queryset = queryset.filter(status=job_status)
            if recruiter_id:
                queryset = queryset.filter(recruiter_id=recruiter_id)

            # Get total count
            total_count = queryset.count()

            # Apply pagination
            jobs = queryset[offset:offset + limit]

            # Serialize data
            job_data = []
            for job in jobs:
                # Get skills for this job
                skills = [jd.jd_skill.name for jd in job.jobdescription_set.all()]

                job_data.append({
                    'id': job.id,
                    'title': job.title,
                    'description': job.description or '',
                    'address': job.address or '',
                    'status': job.status or '',
                    'expiration_date': job.expiration_date,
                    'created_at': job.created_at,
                    'recruiter_id': job.recruiter.id,
                    'company_name': job.recruiter.company_name,
                    'skills': skills
                })

            serializer = JobPostingSerializer(job_data, many=True)

            return Response({
                'success': True,
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['Accounts'])
class AccountView(APIView):
    """
    API endpoint to get all accounts
    GET /accounts/ - List all accounts
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Get query parameters
            account_status = request.GET.get('status', None)
            email = request.GET.get('email', None)
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))

            # Build query
            queryset = Account.objects.all()

            # Apply filters
            if account_status:
                queryset = queryset.filter(status=account_status)
            if email:
                queryset = queryset.filter(email__icontains=email)

            # Get total count
            total_count = queryset.count()

            # Apply pagination
            accounts = queryset[offset:offset + limit]

            # Serialize data
            account_data = []
            for account in accounts:
                account_data.append({
                    'account_id': account.account_id,
                    'email': account.email,
                    'full_name': account.full_name or '',
                    'status': account.status or '',
                })

            serializer = AccountSerializer(account_data, many=True)

            return Response({
                'success': True,
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['Candidates'])
class CandidateView(APIView):
    """
    API endpoint to get all candidates with their skills
    GET /candidates/ - List all candidates joined with resume and skills
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get list of candidates with their skills by joining candidate, resume, and skill tables
        Query params:
        - candidate_id: Filter by specific candidate ID
        - limit: Number of results to return (default: 20)
        - offset: Offset for pagination (default: 0)
        """
        try:
            # Get query parameters
            candidate_id = request.GET.get('candidate_id', None)
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))

            # Build query with prefetch to optimize joins
            queryset = Candidate.objects.select_related('account').prefetch_related(
                Prefetch('resumes', queryset=Resume.objects.prefetch_related('skills'))
            )

            # Apply filters
            if candidate_id:
                queryset = queryset.filter(candidate_id=candidate_id)

            # Get total count
            total_count = queryset.count()

            # Apply pagination
            candidates = queryset[offset:offset + limit]

            # Serialize data
            candidate_data = []
            for candidate in candidates:
                # Collect all skills from all resumes
                skills = []
                for resume in candidate.resumes.all():
                    for skill in resume.skills.all():
                        skills.append({
                            'skill_name': skill.skill_name,
                            'skill_type': skill.skill_type or '',
                            'yearOfExperience': skill.yearOfExperience or 0
                        })

                candidate_data.append({
                    'candidate_id': candidate.candidate_id,
                    'title': candidate.title or '',
                    'fullname': candidate.fullname or '',
                    'email': candidate.account.email,
                    'skills': skills
                })

            serializer = CandidateSerializer(candidate_data, many=True)

            return Response({
                'success': True,
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
