import os, stripe
from fastapi import APIRouter, Request, HTTPException
from .metrics import PAYMENTS_FAILED, PAYMENTS_SUCCEEDED
stripe.api_key=os.getenv("STRIPE_SECRET_KEY"); WEBHOOK_SECRET=os.getenv("STRIPE_WEBHOOK_SECRET")
router=APIRouter(tags=["stripe"])
@router.post("/stripe/webhook")
async def stripe_webhook(request:Request):
    payload=await request.body(); sig=request.headers.get("stripe-signature")
    try: event=stripe.Webhook.construct_event(payload,sig,WEBHOOK_SECRET)
    except Exception as e: raise HTTPException(400,f"invalid webhook: {e}")
    t=event.get("type")
    if t=="payment_intent.succeeded": PAYMENTS_SUCCEEDED.inc()
    elif t=="payment_intent.payment_failed": PAYMENTS_FAILED.inc()
    return {"ok":True}
