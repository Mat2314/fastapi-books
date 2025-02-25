from sqlmodel import Session, select
from db.models import Users
from .base import CRUDBase


class CRUDUser(CRUDBase[Users]):
    def get_by_email(self, db: Session, email: str):
        return db.exec(select(Users).where(Users.email == email)).first()
