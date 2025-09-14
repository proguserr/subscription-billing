
import uuid
from datetime import date
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from ..database import Session
from ..models import SubscriptionCreate
from ..billing import next_period

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("")
async def create_subscription(body: SubscriptionCreate):
    sid = str(uuid.uuid4())
    start, end = next_period(date.today())
    async with Session() as s:
        u = await s.execute(text("SELECT 1 FROM users WHERE id=:id"), {"id": body.user_id})
        if not u.first():
            raise HTTPException(404, "user not found")
        p = await s.execute(text("SELECT 1 FROM plans WHERE code=:c"), {"c": body.plan_code})
        if not p.first():
            raise HTTPException(404, "plan not found")
        await s.execute(text("""INSERT INTO subscriptions(id,user_id,plan_code,status,current_period_start,current_period_end)
                     VALUES (:id,:user,:plan,'active',:ps,:pe)"""),
            {"id":sid,"user":body.user_id,"plan":body.plan_code,"ps":start,"pe":end})
        await s.commit()
    return {"id": sid, "status":"active", "current_period_start": str(start), "current_period_end": str(end)}
