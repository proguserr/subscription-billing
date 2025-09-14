from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI
from starlette.responses import Response
import time
REQUESTS = Counter("api_requests_total","Requests",["method","path","status"])
LAT = Histogram("api_latency_seconds","API latency",["method","path"])
INVOICES_CREATED = Counter("invoices_created_total","Invoices created")
PAYMENTS_SUCCEEDED = Counter("payments_succeeded_total","Stripe payment success")
PAYMENTS_FAILED = Counter("payments_failed_total","Stripe payment failed")
def setup_metrics(app: FastAPI):
    @app.middleware("http")
    async def m(request, call_next):
        start = time.time()
        resp = await call_next(request)
        LAT.labels(request.method, request.url.path).observe(time.time()-start)
        REQUESTS.labels(request.method, request.url.path, resp.status_code).inc()
        return resp
    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
