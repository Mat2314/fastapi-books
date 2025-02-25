from uuid import UUID
from sqlmodel import Session, select
from db.models import Books
from .base import CRUDBase


class CRUDBook(CRUDBase[Books]):
    def get_user_books(
        self, db: Session, author_id: UUID, skip: int = 0, limit: int = 100
    ):
        return db.exec(
            select(Books).where(Books.author_id == author_id).offset(skip).limit(limit)
        ).all()
