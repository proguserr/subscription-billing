
import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from ..database import Session
from ..billing import price_for_plan, usage_charge
from ..metrics import INVOICES_CREATED

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.post("/generate/{user_id}")
async def generate_invoice(user_id: str):
    async with Session() as s:
        res = await s.execute(text("SELECT plan_code,current_period_start,current_period_end FROM subscriptions WHERE user_id=:u AND status='active'"),
                              {"u": user_id})
        row = res.first()
        if not row:
            raise HTTPException(404, "active subscription not found")
        plan_code, ps, pe = row[0], row[1], row[2]

        resu = await s.execute(text("SELECT COALESCE(SUM(quantity),0) FROM usage_events WHERE user_id=:u AND at>=:ps AND at<:pe"),
                               {"u": user_id, "ps": ps, "pe": pe})
        usage = int(resu.scalar() or 0)

        amount = price_for_plan(plan_code) + usage_charge(usage)
        iid = str(uuid.uuid4())
        await s.execute(text("INSERT INTO invoices(id,user_id,period_start,period_end,amount_cents,status) VALUES (:id,:u,:ps,:pe,:amt,'open')"),
                        {"id":iid,"u":user_id,"ps":ps,"pe":pe,"amt":amount})
        await s.commit()
        INVOICES_CREATED.inc()
        return {"id": iid, "user_id": user_id, "amount_cents": amount, "usage": usage}


@router.get("/{user_id}")
async def list_invoices(user_id: str):
    async with Session() as s:
        res = await s.execute(text(
            "SELECT id, user_id, period_start, period_end, amount_cents, status, created_at, paid_at "
            "FROM invoices WHERE user_id=:u ORDER BY created_at DESC"
        ), {"u": user_id})
        rows = res.fetchall()
        return [{
            "id": r[0], "user_id": r[1], "period_start": str(r[2]), "period_end": str(r[3]),
            "amount_cents": r[4], "status": r[5], "created_at": r[6].isoformat(),
            "paid_at": (r[7].isoformat() if r[7] else None)
        } for r in rows]
