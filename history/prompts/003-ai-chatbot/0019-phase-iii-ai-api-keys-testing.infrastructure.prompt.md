---
id: "0019"
title: "Phase III AI API Keys Testing Infrastructure"
stage: "infrastructure"
date: "2026-01-16"
model: "Claude Sonnet 4.5"
surface: "backend"
feature: "ai-chatbot"
branch: "phase-iii-ai-chatbot"
user: "giaic"
command: "sp.testing.api-keys"
labels: ["ai", "api", "keys", "testing", "infrastructure", "validation"]
links:
  spec: "specs/003-ai-chatbot/spec.md"
  plan: "specs/003-ai-chatbot/plan.md"
  tasks: "specs/003-ai-chatbot/tasks.md"
  ticket: null
  adr: null
  pr: null
files:
  - D:\VScode\GitHub\From_Console_to_Cloud\backend\tests\test_all_keys.py
tests: []
prompt_text: |
  Create infrastructure for testing AI API keys across multiple providers (Gemini, Qwen) for Phase III AI Chatbot
response_text: |
  Successfully created AI API keys testing infrastructure:
  - Created test_all_keys.py with async test functions for multiple AI providers
  - Implemented tests for Gemini API (multiple keys) using generativelanguage.googleapis.com
  - Added Qwen API testing capability through portal.qwen.ai
  - Created reusable test function that validates API connectivity and model access
  - Added proper error handling for failed API connections
  - Included test for gemini-2.5-flash and qwen3-coder-plus models
outcome: "Successfully created comprehensive API key testing infrastructure for multiple AI providers"
evaluation: "Testing infrastructure properly validates API connectivity and handles errors appropriately"
---

## AI API Keys Testing Infrastructure

### Summary
Created comprehensive testing infrastructure for validating AI API keys across multiple providers (Google Gemini, Alibaba Qwen) for the Phase III AI Chatbot. This infrastructure allows for validation of API connectivity and model access across different AI service providers.

### Technical Details

#### Test Infrastructure
- Created `test_all_keys.py` with asynchronous testing functions
- Implemented reusable test function that accepts provider-specific parameters
- Added proper error handling for API connectivity issues
- Used AsyncOpenAI client for standardized testing across providers

#### Supported Providers
- **Google Gemini**: Tested with multiple API keys (GEMINI_API_KEY, GEMINI_API_KEY2)
  - Base URL: https://generativelanguage.googleapis.com/v1beta/openai/
  - Model: gemini-2.5-flash
- **Alibaba Qwen**: Tested with QWEN_API_KEY
  - Base URL: https://portal.qwen.ai/v1
  - Model: qwen3-coder-plus

#### Key Features
- Asynchronous testing to handle multiple API calls efficiently
- Provider-agnostic test function that can accommodate new AI services
- Proper error handling and logging for failed connections
- Simple "ping" test to validate API connectivity and model access
- Environment variable integration for secure key management

### Implementation Notes
- All API keys are loaded from environment variables for security
- Test function sends a simple "ping" message to validate connectivity
- Error messages provide specific details about connection failures
- Tests can be run individually or as a suite
- Output clearly identifies which provider and key is being tested

### Testing Steps
1. Set required environment variables (GEMINI_API_KEY, GEMINI_API_KEY2, QWEN_API_KEY)
2. Run the test script: `uv run backend/tests/test_all_keys.py`
3. Verify that each provider returns a valid response
4. Check that error handling works for invalid keys
5. Confirm that all configured models are accessible