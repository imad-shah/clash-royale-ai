import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# Model settings
GPT_MODEL = "gpt-4o"

# Emulator settings
EMULATOR_PORT = 5555

# Analysis settings
MAX_TOKENS = 1000
ANALYSIS_TEMPERATURE = 0.7

# Automation settings
AUTO_PLAY_ENABLED = False
LOOP_DELAY_SECONDS = 3


def validate_config():
    if OPENAI_API_KEY == "api-key-here":
        print("WARNING: OpenAI API key not set!")
        return False
    print("Configuration valid")
    return True
