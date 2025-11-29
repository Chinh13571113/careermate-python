# weaviate_client.py
import weaviate
import os
from dotenv import load_dotenv
from weaviate.classes.init import Auth, Timeout
from typing import Optional

load_dotenv()

class WeaviateClientManager:
    """Quản lý lifecycle của Weaviate client, có thể tái sử dụng trên toàn app."""
    _client: Optional[weaviate.WeaviateClient] = None

    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        if not self.url or not self.api_key:
            raise ValueError("Missing WEAVIATE_URL or WEAVIATE_API_KEY in environment variables.")

    def connect(self):
        """Khởi tạo client nếu chưa tồn tại."""
        if self._client is None:
            print("🔗 Creating new Weaviate client connection...")
            self._client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.url,
                auth_credentials=Auth.api_key(self.api_key),
                additional_config=weaviate.classes.init.AdditionalConfig(
                    timeout=Timeout(init=30, query=60, insert=120)  # Increase timeouts
                )
            )
        return self._client

    def get_client(self):
        """Lấy client hiện tại (tự động connect nếu cần)."""
        if self._client is None:
            return self.connect()
        return self._client

    def close(self):
        """Đóng client khi không còn dùng."""
        if self._client is not None:
            print("🧹 Closing Weaviate client connection...")
            self._client.close()
            self._client = None
