from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class AccountType(str, Enum):
    AUTHOR = "author"
    READER = "reader"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(unique=True, index=True)
    password: str
    account_type: AccountType = Field(default=AccountType.READER)
    
    # Relationship to books (for authors)
    books: List["Book"] = Relationship(back_populates="author")


class Book(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    content: str
    # published: bool = Field(default=False)
    
    # Foreign key to author
    author_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    author: Optional[User] = Relationship(back_populates="books")
