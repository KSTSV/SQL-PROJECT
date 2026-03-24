from fastapi import APIRouter, HTTPException

from app.models.schemas import CollectRequest, CollectResponse
from app.services.collector import run_collection
from app.services.periods import PeriodFormatError

router = APIRouter(prefix="/collect", tags=["collect"])


@router.post("", response_model=CollectResponse)
def collect_data(payload: CollectRequest):
    try:
        return run_collection(
            keyword=payload.keyword,
            period=payload.period,
            max_posts=payload.max_posts,
            load_comments=payload.load_comments,
            comments_per_post_limit=payload.comments_per_post_limit,
            db_name=payload.db_name,
        )
    except PeriodFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
