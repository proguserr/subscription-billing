import os
from celery import Celery
REDIS_URL=os.getenv("REDIS_URL","redis://redis:6379/0")
celery_app=Celery("billing",broker=REDIS_URL,backend=REDIS_URL)
celery_app.conf.update(timezone="UTC",beat_schedule={"monthly-invoicing":{"task":"app.tasks.generate_monthly_invoices","schedule":3600.0}})
