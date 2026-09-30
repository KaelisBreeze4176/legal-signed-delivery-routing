import argparse
import os

from legal_routing.routing_client import InfraiRoutingClient
from legal_routing.routing_policy import (
    MatterRoutingRequest,
    Workload,
    WorkloadRoute,
    choose_signed_delivery_route,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matter-id", required=True)
    parser.add_argument("--intake-capability", required=True)
    parser.add_argument("--delivery-capability", required=True)
    parser.add_argument("--follow-up-capability", required=True)
    parser.add_argument("--exclude-provider", required=True)
    args = parser.parse_args()

    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise SystemExit("Set INFRAI_API_KEY before running this script.")

    request = MatterRoutingRequest(
        matter_id=args.matter_id,
        excluded_provider=args.exclude_provider,
        routes=[
            WorkloadRoute(workload=Workload.MATTER_INTAKE, capability=args.intake_capability),
            WorkloadRoute(
                workload=Workload.SIGNED_DOCUMENT_DELIVERY,
                capability=args.delivery_capability,
            ),
            WorkloadRoute(
                workload=Workload.DEADLINE_FOLLOW_UP,
                capability=args.follow_up_capability,
            ),
        ],
    )
    decision = choose_signed_delivery_route(request)
    routing = InfraiRoutingClient(api_key).exclude_provider(decision)
    print(
        f"Matter {decision.matter_id}: excluded {decision.excluded_provider} "
        f"for {decision.workload.value} ({decision.capability})."
    )
    print(f"Routing response: {routing}")


if __name__ == "__main__":
    main()

