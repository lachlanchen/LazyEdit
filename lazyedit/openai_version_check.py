# openai_version_check.py
import openai
from packaging import version

def check_openai_version():
    required_version = version.parse("1.1.1")
    current_version = version.parse(openai.__version__)

    if current_version < required_version:
        raise ValueError(f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1")
    else:
        print("OpenAI version is compatible.")

# Run the version check when this module is imported
check_openai_version()

# Attempt to import the OpenAI class
from openai import OpenAI

# You might want to initialize the OpenAI client here or in the module where it's imported
# For example:
# client = OpenAI()  # Uncomment and use if initializing OpenAI client directly here
