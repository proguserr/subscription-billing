from fastapi import APIRouter
from sqlalchemy import text
from ..database import Session
router=APIRouter(prefix="/plans",tags=["plans"])
@router.get("")
async def list_plans():
  async with Session() as s:
    res=await s.execute(text("SELECT code,name,amount_cents,interval,trial_days FROM plans ORDER BY amount_cents"))
    return [dict(code=r[0],name=r[1],amount_cents=r[2],interval=r[3],trial_days=r[4]) for r in res.fetchall()]
