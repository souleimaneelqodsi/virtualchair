from flask_restful import Resource
from flask_login import login_user, logout_user, login_required
from flask import request, g
from ..models import UserModel


class RegisterResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return {"error": "Invalid request"}, 400
            if (
                not data.get("email")
                or not data.get("username")
                or not data.get("password")
            ):
                return {"error": "Invalid request"}, 400
            user = UserModel()
            user_data = user.register(data["username"], data["email"], data["password"])
            login_user(user_data)
            return {
                "id": user_data.id,
                "email": user_data.email,
                "username": user_data.username,
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500


class LoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return {"error": "Invalid request"}, 400
            if not data.get("email") or not data.get("password"):
                return {"error": "Invalid request"}, 400
            user = UserModel()
            user_data = user.get_by_email(data["email"])
            if not user_data or not user_data.check_password(data["password"]):
                return {"error": "Invalid credentials"}, 401
            login_user(user_data)
            return {
                "id": user_data.id,
                "email": user_data.email,
                "username": user_data.username,
            }, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500


class LogoutResource(Resource):
    @login_required
    def post(self):
        try:
            logout_user()
            return {"message": "Logged out successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500


class UserByIdResource(Resource):
    @login_required
    def get(self, user_id):
        try:
            if not user_id:
                return {"error": "Invalid request"}, 400
            user = UserModel().get_by_id(user_id)
            if not user:
                return {"message": "Unauthorized"}, 401
            return {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500


class UserByUsernameResource(Resource):
    @login_required
    def get(self, username):
        try:
            if not username:
                return {"error": "Invalid request"}, 400
            user = UserModel().get_by_username(username)
            if not user:
                return {"message": "Unauthorized"}, 401
            return {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500


class UserByEmailResource(Resource):
    @login_required
    def get(self, email):
        try:
            if not email:
                return {"error": "Invalid request"}, 400
            user = UserModel().get_by_email(email)
            if not user:
                return {"message": "Unauthorized"}, 401
            return {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500


class AllUsersResource(Resource):
    @login_required
    def get(self):
        try:
            users = UserModel().get_all_users()
            if len(users) == 0:
                return {"message": "No users found"}, 203
            return {
                "users": [
                    {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                    }
                    for user in users
                ]
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500
