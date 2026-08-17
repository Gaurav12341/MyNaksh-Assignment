from pathlib import Path

from fastapi import APIRouter, Depends, Query

from app.core.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/logs")
async def get_logs(current_user=Depends(require_admin), lines: int = Query(120, ge=1, le=500)):
    log_path = Path(__file__).resolve().parents[2] / "logs" / "app.log"
    if not log_path.exists():
        return {"lines": [], "path": str(log_path)}

    content = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {
        "path": str(log_path),
        "lines": content[-lines:],
    }
