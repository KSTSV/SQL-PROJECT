import time
from datetime import datetime
from pathlib import Path
import duckdb

from app.core.config import settings
from app.core.naming import safe_filename
from app.db.connection import connect
from app.db.schema import init_schema
from app.services.nlp import analyze_text
from app.services.periods import parse_period
from app.services.vk_client import VKClient


class VKCollectorService:
    def __init__(self, db_path: Path, comments_per_post_limit: int = 300):
        self.db_path = db_path
        self.comments_per_post_limit = comments_per_post_limit
        self.con = connect(db_path)
        init_schema(self.con)
        self.vk = VKClient(settings.vk_token, settings.vk_api_version)

    def close(self) -> None:
        self.con.close()

    def get_user_by_vk_id(self, vk_user_id: int):
        return self.con.execute(
            "SELECT user_id, vk_user_id, display_name, profile_url FROM vk_users WHERE vk_user_id = ?",
            [vk_user_id],
        ).fetchone()

    def create_user(self, vk_user_id: int, display_name: str, profile_url: str) -> int:
        user_id = self.con.execute("SELECT nextval('seq_vk_users')").fetchone()[0]
        self.con.execute(
            "INSERT INTO vk_users (user_id, vk_user_id, display_name, profile_url) VALUES (?, ?, ?, ?)",
            [user_id, vk_user_id, display_name, profile_url],
        )
        return user_id

    def get_or_create_user(self, vk_user_id: int, display_name: str, profile_url: str) -> int:
        existing = self.get_user_by_vk_id(vk_user_id)
        if existing:
            user_id = existing[0]
            self.con.execute(
                "UPDATE vk_users SET display_name = ?, profile_url = ? WHERE user_id = ?",
                [display_name, profile_url, user_id],
            )
            return user_id
        return self.create_user(vk_user_id, display_name, profile_url)

    def upsert_users_from_extended(self, profiles, groups) -> dict[int, int]:
        vk_to_local: dict[int, int] = {}
        for p in profiles or []:
            vk_id = int(p["id"])
            display_name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip() or f"id{vk_id}"
            profile_url = self.vk.build_profile_url(vk_id, p.get("screen_name"))
            vk_to_local[vk_id] = self.get_or_create_user(vk_id, display_name, profile_url)
        for g in groups or []:
            vk_id = -int(g["id"])
            display_name = g.get("name", f"club{abs(vk_id)}")
            profile_url = self.vk.build_profile_url(vk_id, g.get("screen_name"))
            vk_to_local[vk_id] = self.get_or_create_user(vk_id, display_name, profile_url)
        return vk_to_local

    def get_post_by_vk_post_id(self, vk_post_id: str):
        return self.con.execute(
            "SELECT post_id FROM vk_posts WHERE vk_post_id = ?",
            [vk_post_id],
        ).fetchone()

    def insert_post(self, vk_post_id: str, author_id: int, published_at: datetime, text: str, like_count: int, comment_count: int) -> int:
        post_id = self.con.execute("SELECT nextval('seq_vk_posts')").fetchone()[0]
        self.con.execute(
            "INSERT INTO vk_posts (post_id, vk_post_id, author_id, published_at, text, like_count, comment_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [post_id, vk_post_id, author_id, published_at, text, like_count, comment_count],
        )
        return post_id

    def insert_post_analysis(self, post_id: int, user_post_id: int, nlp: dict) -> None:
        exists = self.con.execute("SELECT 1 FROM nlp_analysis_posts WHERE post_id = ?", [post_id]).fetchone()
        if exists:
            return
        post_an_id = self.con.execute("SELECT nextval('seq_nlp_analysis_posts')").fetchone()[0]
        self.con.execute(
            """
            INSERT INTO nlp_analysis_posts (
                post_an_id, post_id, user_post_id, n_words, n_inform_word,
                sentiment, sentiment_score, toxicity_score, topics, top
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                post_an_id, post_id, user_post_id, nlp["n_words"], nlp["n_inform_word"],
                nlp["sentiment"], nlp["sentiment_score"], nlp["toxicity_score"], nlp["topics"], nlp["top"],
            ],
        )

    def get_comment_by_vk_comment_id(self, vk_comment_id: str):
        return self.con.execute("SELECT comment_id FROM vk_comments WHERE vk_comment_id = ?", [vk_comment_id]).fetchone()

    def insert_comment(self, vk_comment_id: str, post_id: int, author_id: int, published_at: datetime, text: str, like_count: int) -> int:
        comment_id = self.con.execute("SELECT nextval('seq_vk_comments')").fetchone()[0]
        self.con.execute(
            "INSERT INTO vk_comments (comment_id, vk_comment_id, post_id, author_id, published_at, text, like_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [comment_id, vk_comment_id, post_id, author_id, published_at, text, like_count],
        )
        return comment_id

    def insert_comment_analysis(self, post_id: int, comment_id: int, nlp: dict) -> None:
        exists = self.con.execute("SELECT 1 FROM nlp_analysis_comments WHERE comment_id = ?", [comment_id]).fetchone()
        if exists:
            return
        com_an_id = self.con.execute("SELECT nextval('seq_nlp_analysis_comments')").fetchone()[0]
        self.con.execute(
            """
            INSERT INTO nlp_analysis_comments (
                com_an_id, post_id, comment_id, n_words, n_inform_word,
                sentiment, sentiment_score, toxicity_score, topics
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                com_an_id, post_id, comment_id, nlp["n_words"], nlp["n_inform_word"],
                nlp["sentiment"], nlp["sentiment_score"], nlp["toxicity_score"], nlp["topics"],
            ],
        )

    def search_posts_global(self, query: str, dt_from: datetime, dt_to: datetime, max_posts: int) -> list[int]:
        collected_post_ids: list[int] = []
        next_from = None

        while True:
            remaining = max_posts - len(collected_post_ids)
            if remaining <= 0:
                break

            params = {
                "q": query,
                "extended": 1,
                "count": min(200, remaining),
                "start_time": int(dt_from.timestamp()),
                "end_time": int(dt_to.timestamp()),
                "fields": "screen_name",
            }
            if next_from:
                params["start_from"] = next_from

            resp = self.vk.method("newsfeed.search", params)
            items = resp.get("items", [])
            profiles = resp.get("profiles", [])
            groups = resp.get("groups", [])
            next_from = resp.get("next_from")
            vk_to_local = self.upsert_users_from_extended(profiles, groups)

            if not items:
                break

            for item in items:
                owner_id = int(item["owner_id"])
                vk_post_id = f"{owner_id}_{item['id']}"
                existing = self.get_post_by_vk_post_id(vk_post_id)
                if existing:
                    collected_post_ids.append(existing[0])
                    continue

                author_local_id = vk_to_local.get(owner_id) or self.get_or_create_user(
                    owner_id, f"vk_{owner_id}", self.vk.build_profile_url(owner_id)
                )

                published_at = datetime.fromtimestamp(item["date"])
                text = item.get("text", "")
                like_count = item.get("likes", {}).get("count", 0)
                comment_count = item.get("comments", {}).get("count", 0)

                post_id = self.insert_post(vk_post_id, author_local_id, published_at, text, like_count, comment_count)
                self.insert_post_analysis(post_id, author_local_id, analyze_text(text))
                collected_post_ids.append(post_id)

            if not next_from:
                break
            time.sleep(0.35)

        return collected_post_ids

    def load_comments_for_post(self, post_id: int) -> None:
        row = self.con.execute("SELECT vk_post_id FROM vk_posts WHERE post_id = ?", [post_id]).fetchone()
        if not row:
            return

        owner_id_str, post_vk_id_str = row[0].split("_")
        owner_id, post_vk_id = int(owner_id_str), int(post_vk_id_str)
        offset, loaded = 0, 0

        while loaded < self.comments_per_post_limit:
            batch_size = min(100, self.comments_per_post_limit - loaded)
            try:
                resp = self.vk.method(
                    "wall.getComments",
                    {
                        "owner_id": owner_id,
                        "post_id": post_vk_id,
                        "need_likes": 1,
                        "sort": "asc",
                        "offset": offset,
                        "count": batch_size,
                        "extended": 1,
                        "fields": "screen_name",
                    },
                )
            except Exception:
                break

            items = resp.get("items", [])
            profiles = resp.get("profiles", [])
            groups = resp.get("groups", [])
            if not items:
                break

            vk_to_local = self.upsert_users_from_extended(profiles, groups)
            for item in items:
                comment_vk_id = f"{owner_id}_{post_vk_id}_{item['id']}"
                if self.get_comment_by_vk_comment_id(comment_vk_id):
                    continue

                from_id = int(item.get("from_id", 0))
                author_local_id = vk_to_local.get(from_id) or self.get_or_create_user(
                    from_id, f"vk_{from_id}", self.vk.build_profile_url(from_id)
                )
                text = item.get("text", "")
                comment_id = self.insert_comment(
                    comment_vk_id,
                    post_id,
                    author_local_id,
                    datetime.fromtimestamp(item["date"]),
                    text,
                    item.get("likes", {}).get("count", 0),
                )
                self.insert_comment_analysis(post_id, comment_id, analyze_text(text))

            loaded += len(items)
            offset += len(items)
            if len(items) < batch_size:
                break
            time.sleep(0.35)

    def collect(self, keyword: str, period: str, max_posts: int, load_comments: bool) -> dict:
        dt_from, dt_to = parse_period(period)
        post_ids = self.search_posts_global(keyword, dt_from, dt_to, max_posts)

        if load_comments:
            for post_id in post_ids:
                self.load_comments_for_post(post_id)

        counts = self.con.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM vk_users),
                (SELECT COUNT(*) FROM vk_posts),
                (SELECT COUNT(*) FROM vk_comments),
                (SELECT COUNT(*) FROM nlp_analysis_posts),
                (SELECT COUNT(*) FROM nlp_analysis_comments)
            """
        ).fetchone()
        return {
            "status": "ok",
            "db_path": str(self.db_path),
            "total_users": counts[0],
            "total_posts": counts[1],
            "total_comments": counts[2],
            "total_post_analyses": counts[3],
            "total_comment_analyses": counts[4],
            "total_records": sum(counts),
            "keyword": keyword,
            "period": period,
        }


def make_db_name(keyword: str, period: str) -> str:
    safe_keyword = safe_filename(keyword)
    safe_period = safe_filename(period.replace(':', '_'))
    return f"vk_{safe_keyword}_{safe_period}.duckdb"


def run_collection(keyword: str, period: str, max_posts: int, load_comments: bool, comments_per_post_limit: int, db_name: str | None = None) -> dict:
    db_filename = db_name or make_db_name(keyword, period)
    if not db_filename.endswith('.duckdb'):
        db_filename = f'{db_filename}.duckdb'
    db_path = settings.db_path / db_filename
    service = VKCollectorService(db_path, comments_per_post_limit=comments_per_post_limit)
    try:
        return service.collect(keyword=keyword, period=period, max_posts=max_posts, load_comments=load_comments)
    finally:
        service.close()
