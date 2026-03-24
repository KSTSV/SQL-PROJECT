from pydantic import BaseModel, Field


class CollectRequest(BaseModel):
    keyword: str = Field(..., min_length=1, description="Ключевое слово для поиска по VK")
    period: str = Field(..., description="2025 | 2024-2025 | 2025-01-01:2025-12-31")
    max_posts: int = Field(1200, ge=1, le=10000)
    load_comments: bool = True
    comments_per_post_limit: int = Field(300, ge=0, le=1000)
    db_name: str | None = Field(None, description="Имя файла базы данных без пути")


class CollectResponse(BaseModel):
    status: str
    db_path: str
    total_users: int
    total_posts: int
    total_comments: int
    total_post_analyses: int
    total_comment_analyses: int
    total_records: int
    keyword: str
    period: str
