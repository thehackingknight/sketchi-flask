from dotenv import load_dotenv
import os, cloudinary
load_dotenv()

# Configure cloudinary
cloudinary.config(cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), api_key=os.getenv('CLOUDINARY_API_KEY'), 
    api_secret=os.getenv('CLOUDINARY_API_SECRET'))