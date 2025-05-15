from ..tables import User
from flask import g
import bcrypt
from email_validator import validate_email, EmailNotValidError


class UserModel:
    def register(self, username, email, password):
        if not username or not username.strip():
            raise ValueError("Username is required.")
        if not email or not email.strip():
            raise ValueError("Email is required.")
        if not password:
            raise ValueError("Password is required.")

        processed_username = username.strip().lower()
        processed_email_input = email.strip()

        try:
            validation = validate_email(
                processed_email_input, check_deliverability=False
            )
            normalized_email = validation.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Email is not valid: {str(e)}") from e

        if len(processed_username) > 100:
            raise ValueError("Username is too long (max 100 characters).")
        if len(normalized_email) > 255:
            raise ValueError("Email is too long (max 255 characters).")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        existing_user_by_username = (
            g.db_session.query(User).filter_by(username=processed_username).first()
        )
        if existing_user_by_username:
            raise ValueError("Username already exists.")

        existing_user_by_email = (
            g.db_session.query(User).filter_by(email=normalized_email).first()
        )
        if existing_user_by_email:
            raise ValueError("Email already exists.")

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        new_user = User(
            username=processed_username,
            email=normalized_email,
            password_hash=hashed_password.decode("utf-8"),
        )

        try:
            g.db_session.add(new_user)
            g.db_session.commit()
        except Exception as e:
            g.db_session.rollback()

            raise ValueError(f"Could not register user: {str(e)}") from e

        return new_user

    def login(self, username, password):
        if not username or not password:
            raise ValueError("Username and password are required.")
        user = (
            g.db_session.query(User)
            .filter_by(username=username.strip().lower())
            .first()
        )
        if not user:
            raise ValueError("Invalid username or password.")
        if not bcrypt.checkpw(
            password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            raise ValueError("Invalid username or password.")
        return user

    def get_by_username(self, username):
        if not username:
            raise ValueError("Username is required.")
        return (
            g.db_session.query(User)
            .filter_by(username=username.strip().lower())
            .first()
        )

    def get_by_id(self, id):
        if not id:
            raise ValueError("ID is required.")
        return (
            g.db_session.query(User)
            .filter_by(id=id)
            .first()
        )

    def get_by_email(self, email):
        if not email:
            raise ValueError("Email is required.")
        return (
            g.db_session.query(User)
            .filter_by(email=email.strip().lower())
            .first()
        )
