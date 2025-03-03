from .books import CRUDBooks
from .users import CRUDUsers
from db.models import Users, Books

# Create instances
user_crud = CRUDUsers(Users)
book_crud = CRUDBooks(Books)
