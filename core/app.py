print("--- CONFIRMING APP.PY EXECUTION ---")
import sys
import os

print("DEBUG APP: Starting app execution...")
print("DEBUG APP: Current working directory:", os.getcwd())
print("DEBUG APP: sys.path:", sys.path)


from flask import Flask, send_from_directory, jsonify, abort, request, g, current_app
from flask_restful import Api
from flask_login import LoginManager


import boto3

print("DEBUG APP: Attempting to import Config from .config")
from .config import Config
print("DEBUG APP: Finished importing Config.")


from .database import engine, SessionLocal, Base


from .tables import User


app = Flask(__name__, static_folder="../static", static_url_path="/static")
app.config.from_object(Config)


print(f"DEBUG APP: app.config['SQLALCHEMY_DATABASE_URI'] is: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
if not app.config["SQLALCHEMY_DATABASE_URI"]:
    print("DEBUG APP: SQLALCHEMY_DATABASE_URI is NOT set in app.config, raising error.")
    raise RuntimeError(
        "SQLALCHEMY_DATABASE_URI is not set. Please check your .env file and config.py."
    )
else:
     print("DEBUG APP: SQLALCHEMY_DATABASE_URI IS set in app.config.")


login_manager = LoginManager()
login_manager.init_app(app)


def init_db():
    print("DEBUG APP: Initializing database and creating tables (if they don't exist)...")
    try:
        Base.metadata.create_all(bind=engine)
        print("DEBUG APP: Database tables checked/created successfully.")
    except Exception as e:
        print(f"DEBUG APP: Error creating database tables: {e}")
        print("DEBUG APP: Please ensure your database server is running and accessible,")
        print("DEBUG APP: and that the connection details in your .env file are correct.")
        raise



print("DEBUG APP: Checking AWS config for S3 client initialization.")
if not (
    app.config.get("AWS_ACCESS_KEY_ID")
    and app.config.get("AWS_SECRET_ACCESS_KEY")
    and app.config.get("AWS_REGION")
    and app.config.get("S3_BUCKET_NAME")
):


    setattr(app, 's3_client', None)
    setattr(app, 's3_resource', None)
    app.logger.warning(
        "Warning: AWS S3 credentials, region, or bucket name are not fully set. S3 functionality may be limited."
    )
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

        setattr(app, 's3_client', s3_client)
        setattr(app, 's3_resource', s3_resource)

        app.logger.info("DEBUG APP: S3 client initialized successfully.")
    except Exception as e:

        setattr(app, 's3_client', None)
        setattr(app, 's3_resource', None)
        app.logger.error(f"DEBUG APP: Error initializing S3 client: {e}")


api = Api(app, prefix="/api")


from .controllers import (
    RegisterResource,
    LoginResource,
    LogoutResource,
    UserByIdResource,
    UserByUsernameResource,
    UserByEmailResource,
    AllUsersResource,
    ConferenceDetailResource,
    ConferenceListCreateResource,
    ConferenceUserRolesResource,
    PaperListCreateResource,
    PaperDetailResource,
)

api.add_resource(RegisterResource, "/users/register")
api.add_resource(LoginResource, "/users/login")
api.add_resource(LogoutResource, "/users/logout")
api.add_resource(UserByIdResource, "/users/<string:user_id>")
api.add_resource(UserByUsernameResource, "/users/username/<string:username>")
api.add_resource(UserByEmailResource, "/users/email/<string:email>")
api.add_resource(AllUsersResource, "/users")

api.add_resource(ConferenceListCreateResource, "/conferences")
api.add_resource(ConferenceDetailResource, "/conferences/<string:conf_uuid>")
api.add_resource(ConferenceUserRolesResource, "/conferences/<string:conf_uuid>/my-roles")



api.add_resource(PaperListCreateResource, "/conferences/<string:conf_uuid>/papers")
api.add_resource(PaperDetailResource, "/conferences/<string:conf_uuid>/papers/<string:paper_uuid>")


@app.before_request
def create_session():
    g.db_session = SessionLocal()

    g.s3_client = getattr(current_app, 's3_client', None)
    g.s3_resource = getattr(current_app, 's3_resource', None)




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
            ".css", ".js", ".json", ".txt",
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
            ".woff", ".woff2", ".ttf", ".otf", ".eot",
            ".map"
        ]
        if not any(request.path.lower().endswith(ext) for ext in common_static_extensions) and \
           '.' not in os.path.basename(request.path):
            return send_from_directory(app.static_folder, "index.html"), 200
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):

    app.logger.error(f"Server Error: {error}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


@login_manager.user_loader
def load_user(user_id_str):
    if hasattr(g, "db_session") and g.db_session:
        try:
            return g.db_session.get(User, user_id_str)
        except Exception as e:
            app.logger.error(f"Error in load_user: {e}")
            return None
    return None


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify(
        message="Authentification requise pour accéder à cette ressource."
    ), 401


if __name__ == "__main__":
    print("DEBUG APP: Running in __main__ block.")
    init_db()
    print("DEBUG APP: init_db finished. Starting app run.")

    if engine is None:
        print("DEBUG APP: Database engine failed to initialize. Cannot run app.")
    else:
        app.run(debug=app.config["DEBUG"], host="0.0.0.0", port=8080)
        print("DEBUG APP: app.run finished.")
