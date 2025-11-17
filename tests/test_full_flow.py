from __future__ import annotations

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_crm_flow(client: AsyncClient):
    register_payload = {
        "email": "owner2@example.com",
        "password": "StrongPass123",
        "name": "Owner",
        "organization_name": "Acme",
    }
    response = await client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201, response.text
    tokens = response.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    org_response = await client.get("/api/v1/organizations/me", headers=headers)
    assert org_response.status_code == 200
    organization_id = org_response.json()[0]["id"]
    org_headers = {**headers, "X-Organization-Id": str(organization_id)}

    contact_payload = {"name": "John Doe", "email": "john@example.com", "phone": "+123"}
    contact_resp = await client.post("/api/v1/contacts", json=contact_payload, headers=org_headers)
    assert contact_resp.status_code == 201
    contact_id = contact_resp.json()["id"]

    deal_payload = {
        "contact_id": contact_id,
        "title": "Website redesign",
        "amount": 10000,
        "currency": "USD",
    }
    deal_resp = await client.post("/api/v1/deals", json=deal_payload, headers=org_headers)
    assert deal_resp.status_code == 201
    deal_id = deal_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/deals/{deal_id}",
        json={"status": "won", "stage": "closed"},
        headers=org_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "won"

    task_payload = {
        "deal_id": deal_id,
        "title": "Call client",
        "description": "Discuss next steps",
        "due_date": (date.today() + timedelta(days=1)).isoformat(),
    }
    task_resp = await client.post("/api/v1/tasks", json=task_payload, headers=org_headers)
    assert task_resp.status_code == 201

    summary_resp = await client.get("/api/v1/analytics/deals/summary", headers=org_headers)
    assert summary_resp.status_code == 200, summary_resp.text
    funnel_resp = await client.get("/api/v1/analytics/deals/funnel", headers=org_headers)
    assert funnel_resp.status_code == 200, funnel_resp.text


