from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _assert_ok(resp, code: int = 200):
    assert resp.status_code == code, resp.text
    return resp


def _login(username: str, password: str) -> str:
    resp = _assert_ok(client.post("/api/auth/login", json={"username": username, "password": password}))
    return resp.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_all_routes_smoke():
    hq_token = _login("hq_admin", "Admin@123")
    sh_admin_token = _login("sh_admin", "Admin@123")
    sh_staff_token = _login("sh_staff_01", "Admin@123")

    hq = _headers(hq_token)
    sh_admin = _headers(sh_admin_token)
    sh_staff = _headers(sh_staff_token)

    _assert_ok(client.get("/health"))
    _assert_ok(client.get("/"))
    _assert_ok(client.get("/api/auth/me", headers=hq))

    stores = _assert_ok(client.get("/api/stores", headers=hq)).json()
    assert len(stores) >= 3

    users = _assert_ok(client.get("/api/users", headers=hq)).json()
    assert len(users) >= 3

    services = _assert_ok(client.get("/api/services", headers=sh_admin)).json()
    assert len(services) >= 1
    service_id = services[0]["id"]

    consumables = _assert_ok(client.get("/api/consumables", headers=sh_admin)).json()
    assert len(consumables) >= 1
    consumable_id = consumables[0]["id"]

    members = _assert_ok(client.get("/api/members", headers=sh_admin)).json()
    assert len(members) >= 1
    base_member_id = members[0]["id"]
    base_member_referral_code = members[0]["referral_code"]

    card_plans = _assert_ok(client.get("/api/card-plans", headers=sh_admin)).json()
    assert len(card_plans) >= 1
    annual_plan = next((p for p in card_plans if p["plan_type"] == "annual"), card_plans[0])

    unique = datetime.now().strftime("%Y%m%d%H%M%S")

    created_store = _assert_ok(
        client.post(
            "/api/stores",
            headers=hq,
            json={
                "code": f"T{unique}",
                "name": f"Smoke Store {unique}",
                "city": "Shanghai",
                "address": "Smoke Test Road 1",
                "phone": "021-00000000",
                "is_hq": False,
                "hq_take_rate": 0.12,
            },
        )
    ).json()
    created_store_id = created_store["id"]

    _assert_ok(
        client.post(
            "/api/users",
            headers=hq,
            json={
                "username": f"smoke_user_{unique}",
                "password": "Admin@123",
                "full_name": "Smoke User",
                "role": "employee",
                "store_id": created_store_id,
                "base_salary": 6000,
            },
        )
    )

    created_service = _assert_ok(
        client.post(
            "/api/services",
            headers=hq,
            json={
                "name": f"Smoke Service {unique}",
                "category": "Tuina",
                "scope": "child_and_adult",
                "description": "smoke route coverage",
                "price": 199,
                "active": True,
            },
        )
    ).json()
    created_service_id = created_service["id"]

    created_consumable = _assert_ok(
        client.post(
            "/api/consumables",
            headers=hq,
            json={"name": f"Smoke Consumable {unique}", "unit": "piece", "low_threshold": 10},
        )
    ).json()
    created_consumable_id = created_consumable["id"]

    _assert_ok(
        client.post(
            f"/api/services/{created_service_id}/consumables",
            headers=hq,
            json=[{"consumable_id": created_consumable_id, "quantity": 1, "enabled": True}],
        )
    )

    created_member = _assert_ok(
        client.post(
            "/api/members",
            headers=sh_admin,
            json={
                "name": f"Smoke Member {unique}",
                "phone": "13600000001",
                "wechat_openid": f"wx_smoke_{unique}",
                "gender": "female",
                "store_id": 2,
            },
        )
    ).json()
    created_member_id = created_member["id"]

    _assert_ok(
        client.post(
            f"/api/members/{created_member_id}/children",
            headers=sh_admin,
            json={"name": "Smoke Kid", "gender": "male", "constitution_note": "none"},
        )
    )
    _assert_ok(client.get(f"/api/members/{created_member_id}/children", headers=sh_admin))

    _assert_ok(
        client.post(
            "/api/card-plans",
            headers=hq,
            json={
                "name": f"Smoke Annual {unique}",
                "plan_type": "annual",
                "price": 1888,
                "value_amount": 0,
                "times_total": 0,
                "valid_days": 365,
                "nationwide": True,
                "referral_enabled": True,
            },
        )
    )

    _assert_ok(
        client.post(
            "/api/member-cards/issue",
            headers=sh_admin,
            json={"member_id": created_member_id, "plan_id": annual_plan["id"], "purchase_store_id": 2},
        )
    )
    _assert_ok(client.get(f"/api/member-cards?member_id={created_member_id}", headers=sh_admin))

    created_booking = _assert_ok(
        client.post(
            "/api/bookings",
            headers=sh_admin,
            json={
                "member_id": created_member_id,
                "store_id": 2,
                "service_id": service_id,
                "booking_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "channel": "mini_program",
                "notes": "smoke test",
            },
        )
    ).json()
    created_booking_id = created_booking["id"]

    _assert_ok(client.get("/api/bookings?store_id=2", headers=sh_admin))
    _assert_ok(
        client.patch(
            f"/api/bookings/{created_booking_id}/status",
            headers=sh_admin,
            json={"status": "confirmed"},
        )
    )

    created_order = _assert_ok(
        client.post(
            "/api/orders",
            headers=sh_admin,
            json={
                "member_id": created_member_id,
                "store_id": 2,
                "employee_id": 4,
                "payment_method": "wechat",
                "items": [{"service_id": service_id, "quantity": 1}],
            },
        )
    ).json()
    created_order_id = created_order["id"]

    _assert_ok(client.get(f"/api/orders?member_id={created_member_id}", headers=sh_admin))
    _assert_ok(client.get(f"/api/orders/{created_order_id}/items", headers=sh_admin))

    created_douyin_order = _assert_ok(
        client.post(
            "/api/douyin/orders",
            headers=hq,
            json={
                "dy_order_no": f"DY{unique}",
                "member_name": "Smoke Douyin",
                "phone": "13700000001",
                "amount": 198,
                "city": "Shanghai",
                "assigned_store_id": 2,
            },
        )
    ).json()
    created_douyin_order_id = created_douyin_order["id"]

    _assert_ok(client.get("/api/douyin/orders", headers=hq))
    _assert_ok(client.get("/api/douyin/orders", headers=sh_admin))

    _assert_ok(
        client.post(
            f"/api/douyin/orders/{created_douyin_order_id}/writeoff",
            headers=sh_admin,
            json={"store_id": 2, "employee_id": 4, "member_id": created_member_id, "service_id": service_id},
        )
    )

    _assert_ok(client.get("/api/inventory?store_id=2", headers=sh_admin))
    _assert_ok(
        client.post(
            "/api/inventory/adjust",
            headers=sh_admin,
            json={"store_id": 2, "consumable_id": consumable_id, "change_qty": 10, "reason": "purchase", "note": "smoke"},
        )
    )
    _assert_ok(client.get("/api/inventory/warnings?store_id=2", headers=sh_admin))
    _assert_ok(client.get("/api/inventory/movements?store_id=2", headers=sh_admin))

    _assert_ok(
        client.post(
            "/api/commission-rules",
            headers=sh_admin,
            json={"store_id": 2, "name": f"Smoke Rule {unique}", "min_amount": 1, "max_amount": 999, "rate": 0.1},
        )
    )
    _assert_ok(client.get("/api/commission-rules?store_id=2", headers=sh_admin))

    _assert_ok(client.get("/api/payroll", headers=hq))
    _assert_ok(client.get("/api/payroll", headers=sh_staff))

    created_review = _assert_ok(
        client.post(
            "/api/reviews",
            headers=sh_admin,
            json={
                "member_id": created_member_id,
                "store_id": 2,
                "order_id": created_order_id,
                "rating": 5,
                "content": "great",
                "images": [],
            },
        )
    ).json()
    created_review_id = created_review["id"]

    _assert_ok(client.get("/api/reviews?store_id=2", headers=sh_admin))
    _assert_ok(
        client.post(
            f"/api/reviews/{created_review_id}/reply",
            headers=sh_admin,
            json={"reply_content": "thanks"},
        )
    )
    _assert_ok(
        client.post(
            f"/api/reviews/{created_review_id}/moderate",
            headers=hq,
            json={"is_deleted": False, "is_pinned": True},
        )
    )

    referred_member = _assert_ok(
        client.post(
            "/api/members",
            headers=sh_admin,
            json={
                "name": f"Referred Member {unique}",
                "phone": "13600000002",
                "wechat_openid": f"wx_ref_{unique}",
                "gender": "female",
                "store_id": 2,
                "referral_code": base_member_referral_code,
            },
        )
    ).json()
    referred_member_id = referred_member["id"]

    _assert_ok(
        client.post(
            "/api/member-cards/issue",
            headers=sh_admin,
            json={"member_id": referred_member_id, "plan_id": annual_plan["id"], "purchase_store_id": 2},
        )
    )

    _assert_ok(client.get(f"/api/referrals/records?referrer_member_id={base_member_id}", headers=hq))
    _assert_ok(client.get(f"/api/referrals/{base_member_id}/progress", headers=hq))
    _assert_ok(
        client.post(
            f"/api/referrals/{base_member_id}/approve",
            headers=hq,
            json={"approve": True, "note": "smoke pass"},
        )
    )

    _assert_ok(client.post("/api/settlement/run", headers=hq, json={}))
    _assert_ok(client.get("/api/settlement/records", headers=hq))

    _assert_ok(client.get(f"/api/notifications/{base_member_id}", headers=hq))
    _assert_ok(client.get("/api/dashboard/store/2", headers=sh_admin))
    _assert_ok(client.get("/api/dashboard/hq", headers=hq))
    _assert_ok(client.get("/api/logs", headers=hq))
