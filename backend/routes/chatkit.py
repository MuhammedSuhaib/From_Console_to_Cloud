import os
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["chatkit"])

@router.post("/create-session")
async def create_session(request: Request):
    """
    Proxies the session creation request to OpenAI ChatKit API.
    Required for the frontend component to move past the loading state.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return JSONResponse({"error": "Missing OPENAI_API_KEY"}, status_code=500)

    body = await request.json()
    workflow_id = body.get("workflow", {}).get("id") or os.getenv("CHATKIT_WORKFLOW_ID")
    
    if not workflow_id:
        return JSONResponse({"error": "Missing workflow id"}, status_code=400)

    try:
        async with httpx.AsyncClient(base_url="https://api.openai.com", timeout=10.0) as client:
            response = await client.post(
                "/v1/chatkit/sessions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "OpenAI-Beta": "chatkit_beta=v1",
                    "Content-Type": "application/json",
                },
                json={"workflow": {"id": workflow_id}, "user": "default_user"},
            )
            
            if not response.is_success:
                return JSONResponse({"error": response.text}, status_code=response.status_code)
                
            return JSONResponse(response.json(), status_code=200)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)