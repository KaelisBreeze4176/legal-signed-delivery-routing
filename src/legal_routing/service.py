import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .routing_client import InfraiError, InfraiRoutingClient
from .routing_policy import MatterRoutingRequest, RoutingDecision, choose_signed_delivery_route

service = FastAPI(title="Legal workload provider routing")


class AppliedRouting(BaseModel):
    decision: RoutingDecision
    routing: dict[str, object]


@service.put("/matters/{matter_id}/signed-delivery-provider", response_model=AppliedRouting)
def configure_signed_delivery(matter_id: str, request: MatterRoutingRequest) -> AppliedRouting:
    if matter_id != request.matter_id:
        raise HTTPException(status_code=400, detail="matter_id must match the request body")

    try:
        decision = choose_signed_delivery_route(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="INFRAI_API_KEY is required")

    try:
        result = InfraiRoutingClient(api_key).exclude_provider(decision)
    except InfraiError as exc:
        client_status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(
            status_code=client_status,
            detail={"code": exc.code, "error": exc.detail},
        ) from exc
    except (ConnectionError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AppliedRouting(decision=decision, routing=result)
