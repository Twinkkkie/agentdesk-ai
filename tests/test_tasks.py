import pytest


@pytest.mark.asyncio
async def test_task_crud(client):
    created = await client.post(
        "/api/v1/tasks",
        json={"title": "Ship portfolio", "description": "Finish AgentDesk AI"},
    )
    assert created.status_code == 201
    task = created.json()
    assert task["status"] == "todo"

    fetched = await client.get(f"/api/v1/tasks/{task['id']}")
    assert fetched.status_code == 200

    updated = await client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"status": "in_progress"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "in_progress"

    listed = await client.get("/api/v1/tasks")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = await client.delete(f"/api/v1/tasks/{task['id']}")
    assert deleted.status_code == 204

    missing = await client.get(f"/api/v1/tasks/{task['id']}")
    assert missing.status_code == 404
