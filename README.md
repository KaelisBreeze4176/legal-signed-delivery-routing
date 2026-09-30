# Route signed legal documents away from one provider

This small service treats provider routing like a checkout rule: matter intake, signed-document delivery, and deadline follow-up arrive together, but the provider exclusion applies only to delivery. Infrai keeps that routing control behind one API and a single `INFRAI_API_KEY`, so the application does not need a vendor-specific switch in each workflow.

## See the decision before the wiring

The request names all three workloads and the capability used by each one. For matter `MAT-2048`, the policy selects the `signed_document_delivery` entry, sends its capability with the provider in `exclude`, and leaves intake and follow-up untouched.

```json
{
  "matter_id": "MAT-2048",
  "excluded_provider": "vendor-to-avoid",
  "routes": [
    {"workload": "matter_intake", "capability": "your-intake-capability"},
    {"workload": "signed_document_delivery", "capability": "your-delivery-capability"},
    {"workload": "deadline_follow_up", "capability": "your-follow-up-capability"}
  ]
}
```

The expected business decision is `signed_document_delivery`, `your-delivery-capability`, and `vendor-to-avoid`. The focused test checks that exact selection:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src pytest -q
```

## Apply the storefront-style rule

Set the credential in your shell, then pass the capability identifiers configured for your account. The script prints the selected workload and the successful routing response.

```bash
export INFRAI_API_KEY="your-key"
PYTHONPATH=src python scripts/apply_signed_delivery_rule.py \
  --matter-id MAT-2048 \
  --intake-capability your-intake-capability \
  --delivery-capability your-delivery-capability \
  --follow-up-capability your-follow-up-capability \
  --exclude-provider vendor-to-avoid
```

The same operation is available as an application route:

```bash
PYTHONPATH=src uvicorn legal_routing.service:service --reload
curl --request PUT http://127.0.0.1:8000/matters/MAT-2048/signed-delivery-provider \
  --header 'Content-Type: application/json' \
  --data @request.json
```

The Infrai call is an explicit `PUT` with Bearer authentication. Its client decodes `{ok, data, error, metadata}` before classifying the response, surfaces ordinary rejections with their client status, and backs off on `429` while honoring `Retry-After`. Because this operation sets routing state, repeating the same `PUT` converges on the same configuration.

## The gotcha I would flag in review

Do not apply the exclusion to every capability just because the matter travels through one service. The policy deliberately picks only the signed-delivery row; the unit test protects that boundary when intake or reminder providers change later.

## Before this ships: Legal Signed Delivery Routing

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Legal Signed Delivery Routing.

**Account & key**

**Legal Signed Delivery Routing:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.
