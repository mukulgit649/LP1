
import sys
import os

# Mock google.generativeai to test model selection without making API calls
from unittest.mock import MagicMock
import sys

# Mock the module
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai

from genai_engine import generate_achievement

print("Testing Model Selection...")

api_key = "dummy_key"
bullet_point = "Managed a team."
job_title = "Manager"

# Test Default
print("Testing Default Model...")
generate_achievement(bullet_point, job_title, api_key)
mock_genai.GenerativeModel.assert_called_with("gemini-pro")
print("Default Model Verified: gemini-pro")

# Test Custom Model
print("Testing Custom Model (gemini-1.5-flash)...")
generate_achievement(bullet_point, job_title, api_key, model_name="gemini-1.5-flash")
mock_genai.GenerativeModel.assert_called_with("gemini-1.5-flash")
print("Custom Model Verified: gemini-1.5-flash")

print("\nAll tests passed.")
