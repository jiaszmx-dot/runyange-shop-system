from __future__ import annotations

import json
import random
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from .models import (
    AuditLog,
    CardPlan,
    CommissionRule,
    Consumable,
    InventoryMovement,
    Member,
    MemberCard,
    Notification,
    Order,
    OrderItem,
    OrderStatus,
    PayrollRecord,
    PlanType,
    ReferralReward,
    ReferralStatus,
    ServiceConsumableBinding,
    ServiceItem,
    SettlementRecord,
    Store,
    StoreInventory,
    WriteoffRecord,
)


def now_cn() -> datetime:
    return datetime.now()


def gen_referral_code(member_id: int) -> str:
    return f"RYG{member_id:06d}{random.randint(100, 999)}"


def gen_order_no() -> str:
    return f"RYG{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"


def write_audit_log(db: Session, user_id: int | None, action: str, target_type: str, target_id: str, detail: dict):
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail_json=json.dumps(detail, ensure_ascii=False),
        )
    )


def ensure_inventory_row(db: Session, store_id: int, consumable_id: int, default_threshold: float = 20) -> StoreInventory:
    item = (
        db.query(StoreInventory)
        .filter(StoreInventory.store_id == store_id, StoreInventory.consumable_id == consumable_id)
        .first()
    )
    if item:
        return item
    item = StoreInventory(
        store_id=store_id,
        consumable_id=consumable_id,
        quantity=0,
        warning_threshold=default_threshold,
    )
    db.add(item)
    db.flush()
    return item


def deduct_inventory_for_service(
    db: Session, *, store_id: int, service_id: int, quantity: int, operator_id: int | None, reason_prefix: str = "service"
):
    bindings = (
        db.query(ServiceConsumableBinding)
        .filter(ServiceConsumableBinding.service_id == service_id, ServiceConsumableBinding.enabled.is_(True))
        .all()
    )
    for binding in bindings:
        consumable = db.query(Consumable).filter(Consumable.id == binding.consumable_id).first()
        if not consumable:
            continue
        inventory = ensure_inventory_row(db, store_id, binding.consumable_id, consumable.low_threshold)
        delta = float(binding.quantity) * quantity
        inventory.quantity -= delta
        db.add(
            InventoryMovement(
                store_id=store_id,
                consumable_id=binding.consumable_id,
                change_qty=-delta,
                reason=f"{reason_prefix}_auto_deduction",
                operator_id=operator_id,
                note=f"服务项目#{service_id}",
            )
        )


def select_commission_rate(db: Session, store_id: int | None, monthly_revenue: float) -> float:
    rules = (
        db.query(CommissionRule)
        .filter(
            and_(
                CommissionRule.min_amount <= monthly_revenue,
                CommissionRule.max_amount > monthly_revenue,
                (CommissionRule.store_id == store_id) | CommissionRule.store_id.is_(None),
            )
        )
        .order_by(CommissionRule.store_id.desc())
        .all()
    )
    if not rules:
        return 0
    return float(rules[0].rate)


def recalculate_payroll(db: Session, employee_id: int, store_id: int | None):
    from .models import User

    month = datetime.now().strftime("%Y-%m")
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = (month_start + timedelta(days=35)).replace(day=1)
    monthly_paid = (
        db.query(func.sum(Order.paid_amount))
        .filter(
            Order.employee_id == employee_id,
            Order.created_at >= month_start,
            Order.created_at < month_end,
            Order.status == OrderStatus.PAID,
        )
        .scalar()
        or 0
    )
    rate = select_commission_rate(db, store_id, float(monthly_paid))
    commission = float(monthly_paid) * rate
    payroll = db.query(PayrollRecord).filter(PayrollRecord.employee_id == employee_id, PayrollRecord.month == month).first()
    if payroll:
        payroll.commission = round(commission, 2)
        payroll.total_salary = round(payroll.base_salary + payroll.commission, 2)
        return payroll
    employee = db.query(User).filter(User.id == employee_id).first()
    base_salary = float(employee.base_salary if employee else 0)
    payroll = PayrollRecord(
        employee_id=employee_id,
        month=month,
        base_salary=base_salary,
        commission=round(commission, 2),
        total_salary=round(base_salary + commission, 2),
    )
    db.add(payroll)
    return payroll


def create_order(
    db: Session,
    *,
    member_id: int,
    store_id: int,
    employee_id: int | None,
    payment_method: str,
    items: list[dict],
    paid_amount: float | None,
    from_douyin_order_id: int | None,
):
    if not items:
        raise HTTPException(status_code=400, detail="订单必须包含至少一个服务项目")
    total = 0.0
    normalized_items: list[dict] = []
    for item in items:
        service = db.query(ServiceItem).filter(ServiceItem.id == item["service_id"], ServiceItem.active.is_(True)).first()
        if not service:
            raise HTTPException(status_code=404, detail=f"服务项目不存在: {item['service_id']}")
        qty = int(item["quantity"])
        unit_price = float(item.get("unit_price") or service.price)
        subtotal = round(unit_price * qty, 2)
        total += subtotal
        normalized_items.append(
            {
                "service_id": service.id,
                "quantity": qty,
                "unit_price": unit_price,
                "subtotal": subtotal,
            }
        )

    order = Order(
        order_no=gen_order_no(),
        member_id=member_id,
        store_id=store_id,
        employee_id=employee_id,
        total_amount=round(total, 2),
        paid_amount=round(float(paid_amount if paid_amount is not None else total), 2),
        payment_method=payment_method,
        status=OrderStatus.PAID,
        from_douyin_order_id=from_douyin_order_id,
        is_cross_store=bool(from_douyin_order_id),
    )
    db.add(order)
    db.flush()

    for item in normalized_items:
        db.add(OrderItem(order_id=order.id, **item))
        deduct_inventory_for_service(
            db,
            store_id=store_id,
            service_id=item["service_id"],
            quantity=item["quantity"],
            operator_id=employee_id,
        )

    if employee_id:
        recalculate_payroll(db, employee_id=employee_id, store_id=store_id)

    return order


def run_daily_settlement(db: Session, target_day: date):
    day_end = datetime.combine(target_day, datetime.min.time()) + timedelta(days=1)
    records = (
        db.query(WriteoffRecord)
        .filter(
            WriteoffRecord.settled.is_(False),
            WriteoffRecord.verified_at < day_end,
        )
        .all()
    )
    grouped: dict[int, list[WriteoffRecord]] = {}
    for rec in records:
        grouped.setdefault(rec.verified_store_id, []).append(rec)

    created: list[SettlementRecord] = []
    for store_id, items in grouped.items():
        store = db.query(Store).filter(Store.id == store_id).first()
        rate = float(store.hq_take_rate if store else 0.12)
        total = round(sum(float(item.total_amount) for item in items), 2)
        hq_amount = round(total * rate, 2)
        store_amount = round(total - hq_amount, 2)
        settlement = SettlementRecord(
            settlement_date=target_day,
            store_id=store_id,
            total_amount=total,
            hq_amount=hq_amount,
            store_amount=store_amount,
            item_count=len(items),
        )
        db.add(settlement)
        db.flush()
        created.append(settlement)
        for item in items:
            item.hq_amount = round(float(item.total_amount) * rate, 2)
            item.store_amount = round(float(item.total_amount) - item.hq_amount, 2)
            item.settlement_date = target_day
            item.settled = True
    return created


def process_referral_after_card_issue(db: Session, member_card: MemberCard):
    card_plan = db.query(CardPlan).filter(CardPlan.id == member_card.plan_id).first()
    if not card_plan or card_plan.plan_type != PlanType.ANNUAL:
        return
    member = db.query(Member).filter(Member.id == member_card.member_id).first()
    if not member or not member.referred_by_member_id:
        return

    reward = ReferralReward(
        referrer_member_id=member.referred_by_member_id,
        referred_member_id=member.id,
        referred_card_id=member_card.id,
        status=ReferralStatus.PENDING,
    )
    db.add(reward)
    db.flush()

    progress_count = (
        db.query(func.count(ReferralReward.id))
        .filter(
            ReferralReward.referrer_member_id == member.referred_by_member_id,
            ReferralReward.status.in_(
                [ReferralStatus.PENDING, ReferralStatus.ELIGIBLE, ReferralStatus.APPROVED, ReferralStatus.REFUNDED]
            ),
        )
        .scalar()
        or 0
    )
    referrer = db.query(Member).filter(Member.id == member.referred_by_member_id).first()
    if referrer:
        referrer.referral_success_count = int(progress_count)
        if progress_count >= 5:
            referrer.annual_refund_status = "eligible"
            eligible_rewards = (
                db.query(ReferralReward)
                .filter(
                    ReferralReward.referrer_member_id == referrer.id,
                    ReferralReward.status == ReferralStatus.PENDING,
                )
                .all()
            )
            for r in eligible_rewards:
                r.status = ReferralStatus.ELIGIBLE
            db.add(
                Notification(
                    member_id=referrer.id,
                    title="年卡推荐奖励达成",
                    content="您已完成5名年卡推荐，可提交总部审核并申请1980元退费。",
                    msg_type="referral",
                )
            )


def approve_referral_refund(db: Session, member_id: int, approve: bool, note: str = ""):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    rewards = db.query(ReferralReward).filter(ReferralReward.referrer_member_id == member_id).all()
    now = now_cn()
    if approve:
        member.annual_refund_status = "approved"
        for r in rewards:
            if r.status in [ReferralStatus.ELIGIBLE, ReferralStatus.PENDING]:
                r.status = ReferralStatus.APPROVED
                r.approved_at = now
        db.add(
            Notification(
                member_id=member_id,
                title="推荐奖励审核通过",
                content="总部已审核通过，1980元退费将在3个工作日内处理完成。",
                msg_type="referral",
            )
        )
    else:
        member.annual_refund_status = "rejected"
        for r in rewards:
            if r.status in [ReferralStatus.ELIGIBLE, ReferralStatus.PENDING]:
                r.status = ReferralStatus.REJECTED
                r.note = note


def create_backup(db_url: str):
    if not db_url.startswith("sqlite:///"):
        return None
    db_file = Path(db_url.replace("sqlite:///", ""))
    if not db_file.exists():
        return None
    backup_dir = Path("backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / f"runyangge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copyfile(db_file, backup_file)
    return backup_file
