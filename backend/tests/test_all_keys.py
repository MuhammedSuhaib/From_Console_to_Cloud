import os, asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def test(label, api_key, base_url, model):
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    try:
        r = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
        )
        print(label, "=>", r.choices[0].message.content)
    except Exception as e:
        print(label, "ERROR:", e)

async def main():
    # Gemini key 1
    await test(
        "GEMINI_KEY_1",
        os.getenv("GEMINI_API_KEY"),
        "https://generativelanguage.googleapis.com/v1beta/openai/",
        "gemini-2.5-flash",
    )

    # Gemini key 2
    await test(
        "GEMINI_KEY_2",
        os.getenv("GEMINI_API_KEY2"),
        "https://generativelanguage.googleapis.com/v1beta/openai/",
        "gemini-2.5-flash",
    )

    # Qwen
    await test(
        "QWEN",
        os.getenv("QWEN_API_KEY"),
        "https://portal.qwen.ai/v1",
        "qwen3-coder-plus",
    )

asyncio.run(main())
# uv run backend\tests\test_all_keys.py