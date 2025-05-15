import os
from flask import Flask, send_from_directory, jsonify, abort, request, g
from flask_restful import Api
from flask_login import LoginManager


import boto3

from config import Config

from database import engine, SessionLocal, Base


app = Flask(__name__, static_folder="../static", static_url_path="/static")
app.config.from_object(Config)


if not app.config["SQLALCHEMY_DATABASE_URI"]:
    raise RuntimeError(
        "SQLALCHEMY_DATABASE_URI is not set. Please check your .env file and config.py."
    )


login_manager = LoginManager()


def init_db():
    print("Initializing database and creating tables (if they don't exist)...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        print("Please ensure your database server is running and accessible,")
        print("and that the connection details in your .env file are correct.")
        raise


if not (
    app.config["AWS_ACCESS_KEY_ID"]
    and app.config["AWS_SECRET_ACCESS_KEY"]
    and app.config["AWS_REGION"]
    and app.config["S3_BUCKET_NAME"]
):
    print(
        "Warning: AWS S3 credentials, region, or bucket name are not fully set. S3 functionality may be limited."
    )
    s3_client = None
    s3_resource = None
else:
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
            region_name=app.config["AWS_REGION"],
        )
        s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
            region_name=app.config["AWS_REGION"],
        )
        login_manager.init_app(app)
    except Exception as e:
        print(f"Error initializing S3 client: {e}")
        s3_client = None
        s3_resource = None


api = Api(app, prefix="/api")


from controllers import (
    RegisterResource,
    LoginResource,
    LogoutResource,
    UserByIdResource,
    UserByUsernameResource,
    UserByEmailResource,
    AllUsersResource,
    ConferenceDetailResource,
    ConferenceListCreateResource,
)

api.add_resource(RegisterResource, "/users/register")
api.add_resource(LoginResource, "/users/login")
api.add_resource(LogoutResource, "/users/logout")
api.add_resource(UserByIdResource, "/users/<string:user_id>")
api.add_resource(UserByUsernameResource, "/users/<string:username>")
api.add_resource(UserByEmailResource, "/users/<string:email>")
api.add_resource(AllUsersResource, "/users")

api.add_resource(ConferenceListCreateResource, "/conferences")
api.add_resource(ConferenceDetailResource, "/conferences/<string:conf_id>")


@app.before_request
def create_session():
    g.db_session = SessionLocal()


@app.teardown_appcontext
def close_session(exception=None):
    session = g.pop("db_session", None)
    if session is not None:
        session.close()


@app.route("/")
def serve_index():
    if app.static_folder:
        return send_from_directory(app.static_folder, "index.html")
    abort(500, "Static folder not configured")


@app.route("/<path:path>")
def serve_static_or_spa(path):
    if app.static_folder:
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")
    abort(500, "Static folder not configured")


@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith(api.prefix):
        return jsonify({"error": "API endpoint not found"}), 404

    if app.static_folder and os.path.exists(
        os.path.join(app.static_folder, "index.html")
    ):
        common_static_extensions = [
            ".css",
            ".js",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".json",
            ".txt",
        ]
        if not any(
            request.path.lower().endswith(ext) for ext in common_static_extensions
        ):
            return send_from_directory(app.static_folder, "index.html"), 200
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


@login_manager.user_loader
def load_user(user_id_str):
    """Charge un utilisateur à partir de son ID (stocké dans la session)."""
    from tables import User

    if hasattr(g, "db_session") and g.db_session:
        try:
            return g.db_session.query(User).get(user_id_str)
        except Exception as e:
            print(f"Error in load_user: {e}")
            return None
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Retourne une réponse JSON 401 lorsque @login_required échoue pour une API."""
    return jsonify(
        message="Authentification requise pour accéder à cette ressource."
    ), 401


if __name__ == "__main__":
    init_db()
    app.run(debug=app.config["DEBUG"])
