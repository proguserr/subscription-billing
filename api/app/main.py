from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .metrics import setup_metrics
from .routers.health import router as health
from .routers.users import router as users
from .routers.plans import router as plans
from .routers.subscriptions import router as subs
from .routers.usage import router as usage
from .routers.invoices import router as invoices
from .routers.payments import router as payments
from .stripe_hooks import router as stripe

app = FastAPI(title="Billing & Payments API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

setup_metrics(app)
app.include_router(health)
app.include_router(users)
app.include_router(plans)
app.include_router(subs)
app.include_router(usage)
app.include_router(invoices)
app.include_router(payments)
app.include_router(stripe)
