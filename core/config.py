print("--- CONFIRMING CONFIG.PY IMPORT ---")


import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"DEBUG: Attempting to load .env from: {env_path}")
load_dotenv(env_path)


print(f"DEBUG: After load_dotenv - DB_USER='{os.getenv('DB_USER')}'")
print(f"DEBUG: After load_dotenv - DB_PASSWORD='{os.getenv('DB_PASSWORD')}'")
print(f"DEBUG: After load_dotenv - DB_HOST='{os.getenv('DB_HOST')}'")
print(f"DEBUG: After load_dotenv - DB_PORT='{os.getenv('DB_PORT')}'")
print(f"DEBUG: After load_dotenv - DB_NAME='{os.getenv('DB_NAME')}'")
print(f"DEBUG: After load_dotenv - SECRET_KEY='{os.getenv('SECRET_KEY')}'")

class Config:

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")










    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")

    SQLALCHEMY_DATABASE_URI = None


    print(f"DEBUG Config: Evaluating condition for SQLALCHEMY_DATABASE_URI")
    if DB_USER and DB_PASSWORD and DB_HOST and DB_PORT and DB_NAME:
        print("DEBUG Config: All required DB variables found in Config class attributes. Constructing URI.")
        try:

            encoded_password = quote_plus(DB_PASSWORD)
            SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            )
            print("DEBUG Config: SQLALCHEMY_DATABASE_URI successfully constructed.")
        except Exception as e:
            print(f"DEBUG Config: Error during URI construction: {e}")
            SQLALCHEMY_DATABASE_URI = None
    else:
        print("DEBUG Config: One or more required DB variables NOT found in Config class attributes. SQLALCHEMY_DATABASE_URI will remain None.")


    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY")



    if not SECRET_KEY:
        print("DEBUG Config: SECRET_KEY is NOT set.")


        raise RuntimeError("SECRET_KEY is not set. Please set it in your .env file.")
    else:
         print("DEBUG Config: SECRET_KEY is set.")



    if AWS_REGION and not AWS_REGION.count('-') == 2:
        print(f"Warning: AWS_REGION '{AWS_REGION}' might be in an incorrect format. Expected format like 'eu-north-1'.")
