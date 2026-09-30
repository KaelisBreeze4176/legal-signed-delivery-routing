from enum import Enum

from pydantic import BaseModel, Field


class Workload(str, Enum):
    MATTER_INTAKE = "matter_intake"
    SIGNED_DOCUMENT_DELIVERY = "signed_document_delivery"
    DEADLINE_FOLLOW_UP = "deadline_follow_up"


class WorkloadRoute(BaseModel):
    workload: Workload
    capability: str = Field(min_length=1)


class MatterRoutingRequest(BaseModel):
    matter_id: str = Field(min_length=1)
    excluded_provider: str = Field(min_length=1)
    routes: list[WorkloadRoute] = Field(min_length=1)


class RoutingDecision(BaseModel):
    matter_id: str
    workload: Workload
    capability: str
    excluded_provider: str


def choose_signed_delivery_route(request: MatterRoutingRequest) -> RoutingDecision:
    matches = [
        route
        for route in request.routes
        if route.workload is Workload.SIGNED_DOCUMENT_DELIVERY
    ]
    if len(matches) != 1:
        raise ValueError("provide exactly one signed_document_delivery route")

    route = matches[0]
    return RoutingDecision(
        matter_id=request.matter_id,
        workload=route.workload,
        capability=route.capability,
        excluded_provider=request.excluded_provider,
    )

