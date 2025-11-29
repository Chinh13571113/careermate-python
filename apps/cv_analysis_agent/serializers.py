from rest_framework import serializers


class ResumeUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        required=True,
        help_text="PDF file containing the resume to analyze"
    )
    def validate_file(self, value):
        """Validate that the uploaded file is a PDF"""
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are supported")

        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 10MB")

        return value

class ResumeAnalysisSerializer(serializers.Serializer):
    """
    Serializer cho API upload CV và mô tả công việc (JD)
    để hệ thống phân tích theo chuẩn ATS.
    """
    job_description = serializers.CharField(
        required=True,
        help_text=(
            "Mô tả công việc (Job Description) mà ứng viên muốn so sánh với CV.\n\n"
            "Ví dụ: 'Tuyển dụng Backend Developer có kinh nghiệm với Spring Boot, Docker, AWS, PostgreSQL...'"
        )
    )

    cv_file = serializers.FileField(
        required=True,
        help_text=(
            "File CV hoặc Resume (định dạng .pdf hoặc .docx).\n\n"
            "Ví dụ: 'resume_nguyenvana.pdf'"
        )
    )

    def validate_resume_file(self, value):
        """
        Kiểm tra loại file hợp lệ (PDF hoặc DOCX).
        """
        valid_types = ["application/pdf",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if value.content_type not in valid_types:
            raise serializers.ValidationError("Chỉ chấp nhận file PDF hoặc DOCX.")
        return value

    def validate_job_description(self, value):
        """
        Đảm bảo mô tả công việc không để trống hoặc quá ngắn.
        """
        if len(value.strip()) < 20:
            raise serializers.ValidationError("Mô tả công việc quá ngắn, vui lòng nhập chi tiết hơn.")
        return value