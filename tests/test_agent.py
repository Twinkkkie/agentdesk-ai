import pytest


@pytest.mark.asyncio
async def test_agent_requires_approval_before_mutation(client):
    created = await client.post("/api/v1/tasks", json={"title": "Prepare release"})
    task_id = created.json()["id"]

    triage = await client.post(
        "/api/v1/agent/triage",
        json={"request": f"Mark task #{task_id} done"},
    )
    assert triage.status_code == 201
    run = triage.json()
    assert run["status"] == "proposed"
    assert run["proposed_actions"][0]["action"] == "set_status"

    before = await client.get(f"/api/v1/tasks/{task_id}")
    assert before.json()["status"] == "todo"

    approved = await client.post(f"/api/v1/agent/runs/{run['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()[0]["ok"] is True

    after = await client.get(f"/api/v1/tasks/{task_id}")
    assert after.json()["status"] == "done"
