from flask_restful import Resource
from flask_login import login_user, logout_user
from flask import request, g
from ..models import UserModel


class RegisterResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return {"message": "Invalid request"}, 400
            if (
                not data.get("email")
                or not data.get("username")
                or not data.get("password")
            ):
                return {"message": "Invalid request"}, 400
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
                return {"message": "Invalid request"}, 400
            if not data.get("email") or not data.get("password"):
                return {"message": "Invalid request"}, 400
            user = UserModel()
            user_data = user.get_by_email(data["email"])
            if not user_data or not user_data.check_password(data["password"]):
                return {"message": "Invalid credentials"}, 401
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
    def post(self):
        try:
            logout_user()
            return {"message": "Logged out successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500
