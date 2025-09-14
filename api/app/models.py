from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
class UserCreate(BaseModel): email: str
class SubscriptionCreate(BaseModel): user_id: str; plan_code: str
class UsageEventIn(BaseModel): user_id: str; metric: str; quantity: int
class InvoiceOut(BaseModel):
    id: str; user_id: str; period_start: date; period_end: date
    amount_cents: int; status: str; created_at: datetime; paid_at: Optional[datetime]=None
