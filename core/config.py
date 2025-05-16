print("--- CONFIRMING CONFIG.PY IMPORT ---")


import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"DEBUG: Attempting to load .env from: {env_path}")
load_dotenv(env_path) # Ensures this runs when the module is imported

# Add these debug prints immediately after load_dotenv
print(f"DEBUG: After load_dotenv - DB_USER='{os.getenv('DB_USER')}'")
print(f"DEBUG: After load_dotenv - DB_PASSWORD='{os.getenv('DB_PASSWORD')}'") # Be cautious in production logs
print(f"DEBUG: After load_dotenv - DB_HOST='{os.getenv('DB_HOST')}'")
print(f"DEBUG: After load_dotenv - DB_PORT='{os.getenv('DB_PORT')}'")
print(f"DEBUG: After load_dotenv - DB_NAME='{os.getenv('DB_NAME')}'")
print(f"DEBUG: After load_dotenv - SECRET_KEY='{os.getenv('SECRET_KEY')}'") # Also check SECRET_KEY as Config checks it

class Config:
    # Database config
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    # These prints inside the class might not execute until attributes are accessed,
    # the prints above are more reliable for checking post-load_dotenv status.
    # print(DB_NAME)
    # print(DB_PASSWORD)
    # print(DB_HOST)
    # print(DB_PORT)
    # print(DB_NAME)


    # AWS S3 config
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION") # Should be eu-north-1, not eu-north1

    SQLALCHEMY_DATABASE_URI = None # Initialize to None

    # Add prints inside the conditional logic for URI construction
    print(f"DEBUG Config: Evaluating condition for SQLALCHEMY_DATABASE_URI")
    if DB_USER and DB_PASSWORD and DB_HOST and DB_PORT and DB_NAME:
        print("DEBUG Config: All required DB variables found in Config class attributes. Constructing URI.")
        try:
            # URL-encode the password to handle special characters
            encoded_password = quote_plus(DB_PASSWORD)
            SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            )
            print("DEBUG Config: SQLALCHEMY_DATABASE_URI successfully constructed.")
        except Exception as e:
            print(f"DEBUG Config: Error during URI construction: {e}")
            SQLALCHEMY_DATABASE_URI = None # Ensure it's None on failure
    else:
        print("DEBUG Config: One or more required DB variables NOT found in Config class attributes. SQLALCHEMY_DATABASE_URI will remain None.")


    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

    DEBUG = os.getenv("DEBUG", "False").lower() == "true" # Ensure proper boolean conversion
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Ensure SECRET_KEY is set, Flask-Login requires it
    # This check happens AFTER Config attributes are set
    if not SECRET_KEY:
        print("DEBUG Config: SECRET_KEY is NOT set.")
        # The RuntimeError for SECRET_KEY would happen later in app.py if this isn't raised here.
        # Raising it here makes it clear it's missing.
        raise RuntimeError("SECRET_KEY is not set. Please set it in your .env file.")
    else:
         print("DEBUG Config: SECRET_KEY is set.")


    # Check AWS Region format
    if AWS_REGION and not AWS_REGION.count('-') == 2: # e.g., eu-north-1
        print(f"Warning: AWS_REGION '{AWS_REGION}' might be in an incorrect format. Expected format like 'eu-north-1'.")
