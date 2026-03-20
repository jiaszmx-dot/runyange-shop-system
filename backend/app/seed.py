from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from .models import (
    CardPlan,
    CommissionRule,
    Consumable,
    Member,
    PlanType,
    Role,
    ServiceConsumableBinding,
    ServiceItem,
    Store,
    StoreInventory,
    User,
)
from .security import encrypt_sensitive, get_password_hash
from .services import gen_referral_code


def seed_data(db: Session):
    if db.query(User).count() > 0:
        return

    hq = Store(code="HQ001", name="Runyangge HQ", city="Hangzhou", address="HQ Operations Center", is_hq=True, hq_take_rate=0.15)
    sh = Store(code="SH001", name="Runyangge Shanghai Pudong", city="Shanghai", address="Pudong Example Road 8", hq_take_rate=0.12)
    sz = Store(code="SZ001", name="Runyangge Shenzhen Nanshan", city="Shenzhen", address="Nanshan Health Ave 66", hq_take_rate=0.12)
    db.add_all([hq, sh, sz])
    db.flush()

    users = [
        User(
            username="hq_admin",
            full_name="Headquarter Admin",
            hashed_password=get_password_hash("Admin@123"),
            role=Role.HQ_ADMIN,
            store_id=hq.id,
            base_salary=12000,
        ),
        User(
            username="sh_admin",
            full_name="Shanghai Manager",
            hashed_password=get_password_hash("Admin@123"),
            role=Role.STORE_ADMIN,
            store_id=sh.id,
            base_salary=9500,
        ),
        User(
            username="sz_admin",
            full_name="Shenzhen Manager",
            hashed_password=get_password_hash("Admin@123"),
            role=Role.STORE_ADMIN,
            store_id=sz.id,
            base_salary=9500,
        ),
        User(
            username="sh_staff_01",
            full_name="Therapist Li",
            hashed_password=get_password_hash("Admin@123"),
            role=Role.EMPLOYEE,
            store_id=sh.id,
            base_salary=6500,
        ),
    ]
    db.add_all(users)

    services = [
        ServiceItem(
            name="Pediatric Tuina 45min",
            category="Tuina",
            scope="child",
            description="Digestive and sleep regulation for kids",
            price=198,
        ),
        ServiceItem(
            name="Pediatric Moxibustion 30min",
            category="Moxibustion",
            scope="child",
            description="Warm meridian and immunity support",
            price=168,
        ),
        ServiceItem(
            name="Adult Moxibustion 60min",
            category="Moxibustion",
            scope="adult",
            description="Neck and back stress relief",
            price=268,
        ),
        ServiceItem(
            name="Pediatric Herbal Bath 20min",
            category="Herbal Bath",
            scope="child",
            description="Herbal soothing care",
            price=128,
        ),
    ]
    db.add_all(services)
    db.flush()

    consumables = [
        Consumable(name="Moxa Stick", unit="piece", low_threshold=60),
        Consumable(name="Therapy Oil", unit="ml", low_threshold=500),
        Consumable(name="Herbal Pack", unit="pack", low_threshold=80),
    ]
    db.add_all(consumables)
    db.flush()

    bindings = [
        ServiceConsumableBinding(service_id=services[0].id, consumable_id=consumables[1].id, quantity=20),
        ServiceConsumableBinding(service_id=services[1].id, consumable_id=consumables[0].id, quantity=2),
        ServiceConsumableBinding(service_id=services[2].id, consumable_id=consumables[0].id, quantity=3),
        ServiceConsumableBinding(service_id=services[3].id, consumable_id=consumables[2].id, quantity=1),
    ]
    db.add_all(bindings)

    for store in [sh, sz]:
        for c in consumables:
            db.add(StoreInventory(store_id=store.id, consumable_id=c.id, quantity=300, warning_threshold=c.low_threshold))

    card_plans = [
        CardPlan(name="Stored Card 2000", plan_type=PlanType.STORED_VALUE, price=2000, value_amount=2200, valid_days=730),
        CardPlan(name="10 Sessions Card", plan_type=PlanType.TIMES, price=1680, times_total=10, valid_days=365),
        CardPlan(name="Quarter Wellness Card", plan_type=PlanType.QUARTER, price=1280, times_total=8, valid_days=120),
        CardPlan(
            name="Annual Card 1980 Referral Program",
            plan_type=PlanType.ANNUAL,
            price=1980,
            times_total=0,
            value_amount=0,
            valid_days=365,
            referral_enabled=True,
        ),
    ]
    db.add_all(card_plans)

    commission_rules = [
        CommissionRule(store_id=None, name="Default Tier 1", min_amount=0, max_amount=10000, rate=0.08),
        CommissionRule(store_id=None, name="Default Tier 2", min_amount=10000, max_amount=20000, rate=0.12),
        CommissionRule(store_id=None, name="Default Tier 3", min_amount=20000, max_amount=9999999, rate=0.16),
    ]
    db.add_all(commission_rules)

    member_a = Member(
        name="Parent Wang",
        phone_encrypted=encrypt_sensitive("13800001234"),
        wechat_openid_encrypted=encrypt_sensitive("wx_openid_demo_001"),
        gender="female",
        birthday=date(1990, 8, 1),
        store_id=sh.id,
        referral_code="TEMP_A",
    )
    member_b = Member(
        name="Parent Zhang",
        phone_encrypted=encrypt_sensitive("13900001234"),
        wechat_openid_encrypted=encrypt_sensitive("wx_openid_demo_002"),
        gender="female",
        birthday=date(1992, 5, 2),
        store_id=sz.id,
        referral_code="TEMP_B",
    )
    db.add_all([member_a, member_b])
    db.flush()
    member_a.referral_code = gen_referral_code(member_a.id)
    member_b.referral_code = gen_referral_code(member_b.id)
    member_b.referred_by_member_id = member_a.id
    member_b.annual_refund_status = "pending"

    db.commit()
