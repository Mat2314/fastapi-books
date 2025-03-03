from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from db.crud.base import CRUDBase
from db.models import Books, Users, AccountType


class CRUDBooks(CRUDBase[Books]):
    def create_book(self, db: Session, obj_in: dict, author: Users) -> Books:
        db_obj = Books(**obj_in, author_id=author.id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_books_by_author(
        self, db: Session, author_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Books]:
        return db.exec(
            select(Books)
            .where(Books.author_id == author_id)
            .offset(skip)
            .limit(limit)
        ).all()


books = CRUDBooks(Books)
