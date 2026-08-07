"""HTTP request and response schemas for the Fly-In API."""

from typing import Literal

from pydantic import BaseModel

class HealthResponse(BaseModel):
    """Successful health-check response."""
    
    status: Literal["ok"]
