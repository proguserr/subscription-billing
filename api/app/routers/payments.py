
from fastapi import APIRouter
from sqlalchemy import text
from ..database import Session

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/{user_id}")
async def list_payments(user_id: str):
    async with Session() as s:
        res = await s.execute(text(
            "SELECT p.id, p.invoice_id, p.provider, p.status, p.created_at "
            "FROM payments p JOIN invoices i ON p.invoice_id = i.id "
            "WHERE i.user_id = :u ORDER BY p.created_at DESC"
        ), {"u": user_id})
        rows = res.fetchall()
        return [{
            "id": r[0], "invoice_id": r[1], "provider": r[2], "status": r[3],
            "created_at": r[4].isoformat()
        } for r in rows]
