import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Configuration (loaded from .env file)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model settings
GPT_MODEL = "gpt-4o"

# Screenshot settings
CROP_ENABLED = True
CROP_X = 680
CROP_Y = 31
CROP_WIDTH = 558
CROP_HEIGHT = 953

# Analysis settings
MAX_TOKENS = 1000
ANALYSIS_TEMPERATURE = 0.7


def validate_config():
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not found in .env file!")
        print("Please create a .env file with: OPENAI_API_KEY=your-key-here")
        return False
    print("Configuration valid")
    return True
