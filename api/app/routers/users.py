import uuid
from fastapi import APIRouter
from sqlalchemy import text
from ..database import Session
from ..models import UserCreate
router=APIRouter(prefix="/users",tags=["users"])
@router.post("")
async def create_user(body:UserCreate):
  uid=str(uuid.uuid4())
  async with Session() as s:
    await s.execute(text("INSERT INTO users(id,email) VALUES (:id,:email)"),{"id":uid,"email":body.email})
    await s.commit()
  return {"id":uid,"email":body.email}
