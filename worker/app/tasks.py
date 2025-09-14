
import os, time, uuid
from datetime import timedelta
from prometheus_client import start_http_server, Counter, Histogram
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from .celery_app import celery_app

DATABASE_URL = os.getenv("DATABASE_URL")
PROM_PORT = int(os.getenv("PROM_PORT", "9103"))

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
Session = async_sessionmaker(engine, expire_on_commit=False)

INVOICES_ATTEMPTED = Counter("invoices_attempted_total", "Invoices attempted")
INVOICE_LAT = Histogram("invoice_generation_latency_seconds", "Invoice generation latency")

_started = False

@celery_app.task(name="app.tasks.generate_monthly_invoices")
def generate_monthly_invoices():
    """Generate invoices for subscriptions whose period has ended."""
    global _started
    if not _started:
        try:
            start_http_server(PROM_PORT, addr="0.0.0.0")
            _started = True
        except Exception:
            pass

    import asyncio
    return asyncio.run(_generate())

async def _generate():
    start = time.perf_counter()
    generated = 0
    async with Session() as s:
        res = await s.execute(text("SELECT user_id, plan_code, current_period_start, current_period_end, id FROM subscriptions WHERE status='active' AND current_period_end <= CURRENT_DATE"))
        for (user_id, plan_code, ps, pe, sid) in res.fetchall():
            INVOICES_ATTEMPTED.inc()
            iid = str(uuid.uuid4())
            amount = 9900 if plan_code=='basic' else 19900 if plan_code=='pro' else 49900
            await s.execute(text("INSERT INTO invoices(id,user_id,period_start,period_end,amount_cents,status) VALUES (:id,:u,:ps,:pe,:amt,'open')"),
                            {"id":iid,"u":user_id,"ps":ps,"pe":pe,"amt":amount})
            new_ps = pe
            new_pe = pe + timedelta(days=30)
            await s.execute(text("UPDATE subscriptions SET current_period_start=:ps, current_period_end=:pe WHERE id=:id"),
                            {"ps":new_ps,"pe":new_pe,"id":sid})
            generated += 1
        await s.commit()
    INVOICE_LAT.observe(time.perf_counter() - start)
    return {"generated": generated}
