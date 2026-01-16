# C:\Users\giaic\Desktop\multi_agent\configs\config.py
from agents import OpenAIChatCompletionsModel,AsyncOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
external_client = AsyncOpenAI(api_key=os.getenv("GEMINI_API_KEY"),base_url='https://generativelanguage.googleapis.com/v1beta/openai/')
model_config = OpenAIChatCompletionsModel(model='gemini-2.5-flash',openai_client=external_client)


# ---------------------------
# QWEN CLIENT + MODEL SETUP
# ---------------------------
# external_client = AsyncOpenAI(
#     api_key=os.getenv("QWEN_API_KEY"),
#     base_url="https://portal.qwen.ai/v1",
# )
# model_config = OpenAIChatCompletionsModel(
#     model="qwen3-coder-plus",
#     openai_client=external_client,
# )
