# Hướng dẫn Deploy lên Google Cloud Run

## Yêu cầu

1. Tài khoản Google Cloud Platform
2. Google Cloud CLI đã cài đặt
3. Docker đã cài đặt (để test local)

## Các bước Deploy

### 1. Cài đặt Google Cloud CLI

Tải và cài đặt từ: https://cloud.google.com/sdk/docs/install

### 2. Đăng nhập và cấu hình

```bash
# Đăng nhập
gcloud auth login

# Set project ID
gcloud config set project YOUR_PROJECT_ID

# Enable các API cần thiết
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Chuẩn bị biến môi trường

Tạo file `.env.production` với các biến môi trường:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=Careermate.settings

# Database
POSTGRES_DB=your-db-name
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-db-password
POSTGRES_HOST=your-cloud-sql-instance-connection-name
POSTGRES_PORT=5432

# JWT
SPRING_BOOT_JWT_SECRET=your-jwt-secret

# Celery
CELERY_BROKER_URL=redis://your-redis-url:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-url:6379/0
CELERY_TASK_TIME_LIMIT=1800

# API Keys
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key

# Weaviate
WEAVIATE_URL=your-weaviate-url
WEAVIATE_API_KEY=your-weaviate-api-key
```

### 4. Build và test Docker image locally

```bash
# Build image
docker build -t careermate-backend .

# Test chạy local
docker run -p 8080:8080 --env-file .env.production careermate-backend
```

### 5. Deploy lên Cloud Run (Cách 1 - Đơn giản)

```bash
# Set biến môi trường
gcloud config set project YOUR_PROJECT_ID

# Deploy trực tiếp
gcloud run deploy careermate-backend \
  --source . \
  --region asia-southeast1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=Careermate.settings"
```

### 6. Deploy với Cloud Build (Cách 2 - Nâng cao)

```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml
```

### 7. Cấu hình biến môi trường trên Cloud Run

```bash
# Set secrets từ Secret Manager
gcloud run services update careermate-backend \
  --region asia-southeast1 \
  --update-secrets=SPRING_BOOT_JWT_SECRET=spring-boot-jwt-secret:latest,\
SECRET_KEY=django-secret-key:latest,\
POSTGRES_PASSWORD=postgres-password:latest
```

### 8. Kết nối với Cloud SQL

```bash
# Tạo Cloud SQL instance
gcloud sql instances create careermate-postgres \
  --database-version=POSTGRES_14 \
  --tier=db-g1-small \
  --region=asia-southeast1

# Kết nối Cloud Run với Cloud SQL
gcloud run services update careermate-backend \
  --region asia-southeast1 \
  --add-cloudsql-instances YOUR_PROJECT_ID:asia-southeast1:careermate-postgres
```

### 9. Migration database

```bash
# Chạy migrations
gcloud run jobs create careermate-migrate \
  --image gcr.io/YOUR_PROJECT_ID/careermate-backend:latest \
  --region asia-southeast1 \
  --command python \
  --args manage.py,migrate

gcloud run jobs execute careermate-migrate --region asia-southeast1
```

## Cấu hình Redis (cho Celery)

### Option 1: Google Cloud Memorystore

```bash
gcloud redis instances create careermate-redis \
  --size=1 \
  --region=asia-southeast1 \
  --redis-version=redis_6_x
```

### Option 2: Upstash Redis (Serverless)

Sử dụng Upstash Redis cho serverless deployment: https://upstash.com/

## Monitoring và Logging

```bash
# Xem logs
gcloud run services logs read careermate-backend --region asia-southeast1

# Xem logs realtime
gcloud run services logs tail careermate-backend --region asia-southeast1
```

## Cập nhật service

```bash
# Cập nhật với image mới
gcloud run services update careermate-backend \
  --image gcr.io/YOUR_PROJECT_ID/careermate-backend:latest \
  --region asia-southeast1
```

## Chi phí ước tính

- Cloud Run: ~$0.00002400/vCPU-second, ~$0.00000250/GiB-second
- Cloud SQL: ~$7-50/month (tùy tier)
- Redis Memorystore: ~$30/month (1GB)
- Container Registry: ~$0.026/GB/month

## Lưu ý quan trọng

1. **Cold Start**: Cloud Run có thể có cold start time ~10-30s do ML models. Set `--min-instances 1` để giảm cold start.

2. **Memory**: ML models (torch, transformers) cần nhiều RAM. Recommend ít nhất 2GB memory.

3. **Timeout**: Set timeout cao (300s) cho các task ML processing lâu.

4. **Celery Worker**: Celery worker cần deploy riêng (không thể chạy trên Cloud Run). Consider:
   - Google Cloud Tasks
   - Cloud Functions cho async tasks
   - Separate Celery worker trên Compute Engine/GKE

5. **Static Files**: Sử dụng Google Cloud Storage cho static files trong production.

6. **Database**: Cloud SQL có thể tốn kém. Consider:
   - Cloud SQL (managed PostgreSQL)
   - AlloyDB (performance cao hơn)
   - Neon/Supabase (serverless postgres)

## Troubleshooting

### Container fails to start
```bash
# Check logs
gcloud run services logs read careermate-backend --region asia-southeast1 --limit 50

# Check revisions
gcloud run revisions list --service careermate-backend --region asia-southeast1
```

### Database connection issues
- Verify Cloud SQL connection name
- Check VPC connector (if using private IP)
- Verify credentials in Secret Manager

### High memory usage
- Monitor memory usage in Cloud Console
- Increase memory allocation if needed
- Optimize ML model loading

## Liên hệ

Nếu có vấn đề, tham khảo:
- Google Cloud Run docs: https://cloud.google.com/run/docs
- Django deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/

