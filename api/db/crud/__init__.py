from .books import CRUDBook
from .users import CRUDUser
from db.models import Users, Books

# Create instances
user_crud = CRUDUser(Users)
book_crud = CRUDBook(Books)
