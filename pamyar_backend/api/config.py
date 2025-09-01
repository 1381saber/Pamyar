# api/config.py

import os
from dotenv import load_dotenv

load_dotenv() 

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# نام مدل جمینی
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# تنظیمات تولید محتوا
GENERATION_CONFIG = {
    "temperature": 0.9, 
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024, 
}
# ...