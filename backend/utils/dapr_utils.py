"""
Dapr utility functions for cloud-ready applications.
Provides graceful fallback when Dapr sidecar is not available.
"""
import os
import logging
import requests
import json

logger = logging.getLogger(__name__)

def dapr_http_fallback(endpoint: str, method: str = "POST", data=None, headers=None):
    """
    Generic Dapr HTTP fallback function.
    Tries to use Dapr sidecar, falls back gracefully if not available.

    Args:
        endpoint: Dapr endpoint (e.g., "/v1.0/publish/pubsub_name/topic_name")
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Data to send in request body
        headers: Additional headers to send

    Returns:
        Response from Dapr or fallback, or None if both fail
    """
    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
    dapr_url = f"http://localhost:{dapr_port}{endpoint}"

    # Check if Dapr sidecar is available
    try:
        dapr_health_url = f"http://localhost:{dapr_port}/v1.0/healthz"
        health_response = requests.get(dapr_health_url, timeout=2)

        if health_response.status_code == 200:
            # Dapr sidecar is available, use it
            req_headers = headers or {}
            req_headers["Content-Type"] = "application/json"

            if method.upper() == "POST":
                response = requests.post(dapr_url, json=data, headers=req_headers, timeout=10)
            elif method.upper() == "GET":
                response = requests.get(dapr_url, headers=req_headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(dapr_url, json=data, headers=req_headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(dapr_url, headers=req_headers, timeout=10)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            if response.status_code in [200, 204]:
                logger.debug(f"Dapr call successful: {method} {endpoint}")
                return response
            else:
                logger.warning(f"Dapr call failed with status {response.status_code}, endpoint: {endpoint}")
                return None
        else:
            logger.warning(f"Dapr sidecar not available, skipping Dapr call to {endpoint}")
            return None
    except requests.exceptions.RequestException:
        logger.warning(f"Dapr sidecar not available, skipping Dapr call to {endpoint}")
        return None
    except Exception as e:
        logger.warning(f"Dapr unavailable for {endpoint}: {str(e)}")
        return None