import typer
import random
from faker import Faker
from db.database import init_db, engine
from db.models import Users, Books, AccountType
from sqlmodel import Session, select, delete
from core.security import get_password_hash

app = typer.Typer()
fake = Faker()


def create_random_user(db: Session) -> Users:
    while True:
        email = fake.email()
        # Check if email already exists
        existing_user = db.exec(
            select(Users).where(Users.email == email)
        ).first()
        if not existing_user:
            break

    # Generate a plain password and hash it
    plain_password = fake.password()
    print(f"Email: {email} - Plain password: {plain_password}")
    hashed_password = get_password_hash(plain_password)

    user = Users(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=email,
        password=hashed_password,  # Store the hashed password
        account_type=random.choice([AccountType.AUTHOR, AccountType.READER]),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_random_books(db: Session, author: Users, num_books: int) -> None:
    for _ in range(num_books):
        book = Books(
            title=fake.catch_phrase(),
            content=fake.text(max_nb_chars=2000),
            author_id=author.id,
        )
        db.add(book)
    db.commit()


@app.command()
def populate(num_users: int = typer.Argument(..., help="Number of users to create")):
    """
    Populate database with sample data.
    Example: python scripts/db.py populate 1000
    """
    init_db()

    with Session(engine) as db:
        for i in range(num_users):
            user = create_random_user(db)

            # If user is an author, create random number of books (0-10)
            if user.account_type == AccountType.AUTHOR:
                num_books = random.randint(0, 10)
                create_random_books(db, user, num_books)

            if i % 100 == 0:
                typer.echo(f"Created {i} users...")

        typer.echo(f"Successfully created {num_users} users!", color=typer.colors.GREEN)


@app.command()
def clean():
    """
    Clean the database.
    Example: python scripts/db.py clean
    """
    with Session(engine) as db:
        db.exec(delete(Books))
        db.exec(delete(Users))
        db.commit()
    typer.echo("Database cleaned!", color=typer.colors.GREEN)


if __name__ == "__main__":
    app()
