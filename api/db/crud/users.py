from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from db.crud.base import CRUDBase
from db.models import Users
from core.security import get_password_hash, verify_password


class CRUDUsers(CRUDBase[Users]):
    def create(self, db: Session, obj_in: dict) -> Users:
        # Create a new dict without the password
        obj_data = {k: v for k, v in obj_in.items() if k != "password"}
        # Add the hashed password
        obj_data["password"] = get_password_hash(obj_in["password"])
        
        db_obj = Users(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, email: str, password: str) -> Optional[Users]:
        print("\nAuthenticating user...")
        user = db.exec(select(Users).where(Users.email == email)).first()
        print("Found user:", user is not None)
        if user:
            print("User details:", {
                "email": user.email,
                "stored_password": user.password,
                "account_type": user.account_type
            })
            print("Verifying password...")
            is_valid = verify_password(password, user.password)
            print("Password valid:", is_valid)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def get_by_email(self, db: Session, email: str) -> Optional[Users]:
        return db.exec(select(Users).where(Users.email == email)).first()


users = CRUDUsers(Users)
