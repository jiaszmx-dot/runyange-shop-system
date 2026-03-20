from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.seed import seed_data
from main import app

db_file = Path("runyangge.db")
if db_file.exists():
    db_file.unlink()
Base.metadata.create_all(bind=engine)
with SessionLocal() as setup_db:
    seed_data(setup_db)


client = TestClient(app)


def login(username: str, password: str) -> str:
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_core_business_flow():
    hq_token = login("hq_admin", "Admin@123")
    store_token = login("sh_admin", "Admin@123")

    hq_headers = {"Authorization": f"Bearer {hq_token}"}
    store_headers = {"Authorization": f"Bearer {store_token}"}

    members = client.get("/api/members", headers=store_headers).json()
    assert len(members) >= 1
    member_id = members[0]["id"]

    services = client.get("/api/services", headers=store_headers).json()
    assert len(services) >= 1
    service_id = services[0]["id"]

    before_inventory = client.get("/api/inventory?store_id=2", headers=hq_headers).json()
    assert len(before_inventory) >= 1

    order_payload = {
        "member_id": member_id,
        "store_id": 2,
        "employee_id": 4,
        "payment_method": "wechat",
        "items": [{"service_id": service_id, "quantity": 1}],
    }
    order_resp = client.post("/api/orders", json=order_payload, headers=store_headers)
    assert order_resp.status_code == 200, order_resp.text

    after_inventory = client.get("/api/inventory?store_id=2", headers=hq_headers).json()
    assert len(after_inventory) >= 1

    dy_payload = {
        "dy_order_no": f"DY{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "member_name": "测试抖音用户",
        "phone": "13700001111",
        "amount": 198,
        "city": "上海",
        "assigned_store_id": 2,
    }
    dy_resp = client.post("/api/douyin/orders", json=dy_payload, headers=hq_headers)
    assert dy_resp.status_code == 200, dy_resp.text
    dy_id = dy_resp.json()["id"]

    writeoff_resp = client.post(
        f"/api/douyin/orders/{dy_id}/writeoff",
        json={"store_id": 2, "employee_id": 4, "member_id": member_id, "service_id": service_id},
        headers=store_headers,
    )
    assert writeoff_resp.status_code == 200, writeoff_resp.text

    settlement_resp = client.post("/api/settlement/run", json={}, headers=hq_headers)
    assert settlement_resp.status_code == 200, settlement_resp.text

    settlement_records = client.get("/api/settlement/records", headers=hq_headers).json()
    assert isinstance(settlement_records, list)
    assert len(settlement_records) >= 1
