from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import boto3

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

s3_client = boto3.client('s3',
                         aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                         region_name=Config.AWS_REGION)

# Placeholder for table creation scripts
# from models import Bas
# Base.metadata.create_all(bind=db.engine)

# Example route
@app.route('/')
def home():
    return "Welcome to the Flask App!"

# Import and use s3_client in other modules
# Example: from app import s3_client
