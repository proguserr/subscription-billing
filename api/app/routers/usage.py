from fastapi import APIRouter
from sqlalchemy import text
from ..database import Session
from ..models import UsageEventIn
router=APIRouter(prefix="/usage",tags=["usage"])
@router.post("")
async def track_usage(body:UsageEventIn):
  async with Session() as s:
    await s.execute(text("INSERT INTO usage_events(user_id,metric,quantity) VALUES (:u,:m,:q)"),{"u":body.user_id,"m":body.metric,"q":body.quantity})
    await s.commit()
  return {"ok":True}
