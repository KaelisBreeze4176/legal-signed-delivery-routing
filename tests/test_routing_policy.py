from legal_routing.routing_policy import (
    MatterRoutingRequest,
    Workload,
    WorkloadRoute,
    choose_signed_delivery_route,
)


def test_only_signed_delivery_drives_the_provider_exclusion() -> None:
    request = MatterRoutingRequest(
        matter_id="MAT-2048",
        excluded_provider="vendor-to-avoid",
        routes=[
            WorkloadRoute(workload=Workload.MATTER_INTAKE, capability="intake-capability"),
            WorkloadRoute(
                workload=Workload.SIGNED_DOCUMENT_DELIVERY,
                capability="delivery-capability",
            ),
            WorkloadRoute(
                workload=Workload.DEADLINE_FOLLOW_UP,
                capability="follow-up-capability",
            ),
        ],
    )

    decision = choose_signed_delivery_route(request)

    assert decision.matter_id == "MAT-2048"
    assert decision.workload is Workload.SIGNED_DOCUMENT_DELIVERY
    assert decision.capability == "delivery-capability"
    assert decision.excluded_provider == "vendor-to-avoid"

