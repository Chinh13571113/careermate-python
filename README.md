
---

## ⚡ Chi tiết các folder quan trọng

### 1. `agent/config/`
Chứa các cấu hình kết nối và client:
- `weaviate_config.py`: Khởi tạo client, URL, schema cho Weaviate.  
- `embedding_config.py`: Khởi tạo model embedding, API key

### 2. `agent/agents/`
Mỗi file tương ứng một **agent độc lập**:
- **roadmap_agent**: Tạo roadmap học tập dựa trên kỹ năng hiện có & target role.  
- **recommendation_agent**: Truy xuất và gợi ý job dựa trên CV hoặc skills.  
- **cv_creation_agent**: Xử lý CV, normalize skills, tạo JSON chuẩn.

### 3. `agent/chains/`
Chain liên kết **prompt, LLM, tool** thành pipeline logic:
- Ví dụ: roadmap_chain gọi roadmap_agent → prompt → internal/external tools → output JSON.

### 4. `agent/tools/`
- `internal/`: Tools gọi Weaviate, database, hoặc các chức năng nội bộ.  
- `external/`: Tools gọi API bên ngoài (Wikipedia, TMDB, weather, v.v.).
- Các tool nên được wrapper trong internal/external để agent chỉ cần gọi agent.run() mà không biết chi tiết implementation.

### 5. `agent/prompts/`
Chứa các prompt template để agent biết cách format input/output và tạo JSON chuẩn.

### 6. `agent/utils/`
Các hàm helper: logging, parse JSON, validate data, handle errors, v.v.

### 7. `agent/llm/`
Wrapper cho các LLM:
- Khởi tạo LLM, setting temperature, max token.
- Mỗi agent có thể import cùng một LLM fine-tuned.

### 8. `agent/data/`
- Chứa embeddings, dataset để fine-tune, hoặc ví dụ input/output JSON.  
- Phục vụ agent cho training hoặc thử nghiệm local.
- Data và embeddings không commit trực tiếp vào Git nếu có PII hoặc dataset lớn.

### 9. `mypermit/`
- Client Permit.io để kiểm soát quyền hạn agent/user.  
- Bảo vệ agent khỏi việc thao tác dữ liệu ngoài quyền.

### 10. `apps/api/`
- Django REST API: nhận request từ spring boot, gọi agent và trả kết quả.  
- `views.py` + `urls.py` định tuyến endpoints.

---

## ⚡ Hướng dẫn nhanh dev

1. **Cài đặt môi trường**
```bash
1. 
uv venv --python 3.12 (đã có thì không cần chạy)
source .venv/bin/activate
uv pip install -r requirements.txt

2. Chạy Weaviate local

docker compose up -d

3. Chạy Django server

python manage.py migrate
python manage.py runserver