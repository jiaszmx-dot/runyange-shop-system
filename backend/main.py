from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import DATABASE_URL, Base, engine, get_db
from app.models import (
    Booking,
    CardPlan,
    ChildProfile,
    CommissionRule,
    Consumable,
    DouyinOrder,
    InventoryMovement,
    Member,
    MemberCard,
    Notification,
    Order,
    OrderItem,
    ReferralReward,
    Review,
    Role,
    ServiceConsumableBinding,
    ServiceItem,
    SettlementRecord,
    Store,
    StoreInventory,
    User,
    WriteoffRecord,
)
from app.schemas import (
    BookingCreate,
    BookingStatusUpdate,
    CardPlanCreate,
    ChildCreate,
    CommissionRuleCreate,
    ConsumableBindInput,
    ConsumableCreate,
    DouyinOrderCreate,
    InventoryAdjustRequest,
    IssueCardRequest,
    LoginRequest,
    MemberCreate,
    OrderCreate,
    ReferralApproveRequest,
    ReviewCreate,
    ReviewModeration,
    ReviewReply,
    ServiceCreate,
    SettlementRunRequest,
    StoreCreate,
    TokenResponse,
    UserCreate,
    WriteoffRequest,
)
from app.security import (
    create_access_token,
    decrypt_sensitive,
    encrypt_sensitive,
    get_current_user,
    get_password_hash,
    require_roles,
    verify_password,
)
from app.seed import seed_data
from app.services import (
    approve_referral_refund,
    create_backup,
    create_order,
    gen_referral_code,
    process_referral_after_card_issue,
    run_daily_settlement,
    write_audit_log,
)

app = FastAPI(title="润阳阁云店铺系统 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


def serialize_member(member: Member):
    return {
        "id": member.id,
        "name": member.name,
        "phone": decrypt_sensitive(member.phone_encrypted),
        "wechat_openid": decrypt_sensitive(member.wechat_openid_encrypted),
        "gender": member.gender,
        "birthday": member.birthday,
        "store_id": member.store_id,
        "referral_code": member.referral_code,
        "referred_by_member_id": member.referred_by_member_id,
        "referral_success_count": member.referral_success_count,
        "annual_refund_status": member.annual_refund_status,
    }


def _scheduled_settlement():
    db = next(get_db())
    try:
        run_daily_settlement(db, date.today())
        db.commit()
    finally:
        db.close()


def _scheduled_backup():
    _ = create_backup(DATABASE_URL)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        seed_data(db)

    if not scheduler.running:
        scheduler.add_job(_scheduled_settlement, "cron", hour=0, minute=0, id="daily_settlement", replace_existing=True)
        scheduler.add_job(_scheduled_backup, "cron", hour=0, minute=10, id="daily_backup", replace_existing=True)
        scheduler.start()


@app.on_event("shutdown")
def on_shutdown():
    if scheduler.running:
        scheduler.shutdown(wait=False)


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.get("/")
def root():
    return {
        "service": "润阳阁云店铺系统 API",
        "docs": "/docs",
        "health": "/health",
        "frontend": "http://127.0.0.1:5173",
    }


@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": user.username, "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role, username=user.username, store_id=user.store_id)


@app.get("/api/auth/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "store_id": user.store_id,
        "base_salary": user.base_salary,
    }


@app.post("/api/users")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN, Role.STORE_ADMIN)),
):
    if user.role == Role.STORE_ADMIN and payload.role == Role.HQ_ADMIN:
        raise HTTPException(status_code=403, detail="门店管理员不能创建总部账号")
    if user.role == Role.STORE_ADMIN:
        payload.store_id = user.store_id
    existed = db.query(User).filter(User.username == payload.username).first()
    if existed:
        raise HTTPException(status_code=409, detail="账号已存在")
    new_user = User(
        username=payload.username,
        full_name=payload.full_name,
        role=payload.role,
        store_id=payload.store_id,
        hashed_password=get_password_hash(payload.password),
        base_salary=payload.base_salary,
    )
    db.add(new_user)
    write_audit_log(db, user.id, "user.create", "user", payload.username, payload.model_dump())
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/users")
def list_users(
    store_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN, Role.STORE_ADMIN)),
):
    q = db.query(User)
    if user.role == Role.STORE_ADMIN:
        q = q.filter(User.store_id == user.store_id)
    elif store_id:
        q = q.filter(User.store_id == store_id)
    return q.order_by(User.id.desc()).all()


@app.post("/api/stores")
def create_store(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    store = Store(**payload.model_dump())
    db.add(store)
    write_audit_log(db, user.id, "store.create", "store", payload.code, payload.model_dump())
    db.commit()
    db.refresh(store)
    return store


@app.get("/api/stores")
def list_stores(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        return db.query(Store).filter(Store.id == user.store_id).all()
    return db.query(Store).order_by(Store.id.asc()).all()


@app.post("/api/services")
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    service = ServiceItem(**payload.model_dump())
    db.add(service)
    write_audit_log(db, user.id, "service.create", "service", payload.name, payload.model_dump())
    db.commit()
    db.refresh(service)
    return service


@app.get("/api/services")
def list_services(active_only: bool = True, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(ServiceItem)
    if active_only:
        q = q.filter(ServiceItem.active.is_(True))
    return q.order_by(ServiceItem.id.asc()).all()


@app.post("/api/consumables")
def create_consumable(
    payload: ConsumableCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    item = Consumable(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/consumables")
def list_consumables(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Consumable).order_by(Consumable.id.asc()).all()


@app.post("/api/services/{service_id}/consumables")
def bind_consumable(
    service_id: int,
    payload: list[ConsumableBindInput],
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    service = db.query(ServiceItem).filter(ServiceItem.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="服务项目不存在")
    db.query(ServiceConsumableBinding).filter(ServiceConsumableBinding.service_id == service_id).delete()
    for row in payload:
        db.add(
            ServiceConsumableBinding(
                service_id=service_id,
                consumable_id=row.consumable_id,
                quantity=row.quantity,
                enabled=row.enabled,
            )
        )
    write_audit_log(db, user.id, "service.bind_consumables", "service", str(service_id), {"count": len(payload)})
    db.commit()
    return {"ok": True}


@app.post("/api/members")
def create_member(payload: MemberCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == Role.MEMBER:
        raise HTTPException(status_code=403, detail="无权限")
    store_id = payload.store_id or user.store_id
    referred_by_member_id = None
    if payload.referral_code:
        referrer = db.query(Member).filter(Member.referral_code == payload.referral_code).first()
        if referrer:
            referred_by_member_id = referrer.id
    member = Member(
        name=payload.name,
        phone_encrypted=encrypt_sensitive(payload.phone),
        wechat_openid_encrypted=encrypt_sensitive(payload.wechat_openid),
        gender=payload.gender,
        birthday=payload.birthday,
        store_id=store_id,
        referral_code="TEMP",
        referred_by_member_id=referred_by_member_id,
    )
    db.add(member)
    db.flush()
    member.referral_code = gen_referral_code(member.id)
    write_audit_log(db, user.id, "member.create", "member", str(member.id), {"name": payload.name})
    db.commit()
    db.refresh(member)
    return serialize_member(member)


@app.get("/api/members")
def list_members(
    store_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Member)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(Member.store_id == user.store_id)
    elif store_id:
        q = q.filter(Member.store_id == store_id)
    members = q.order_by(Member.id.desc()).all()
    return [serialize_member(m) for m in members]


@app.post("/api/members/{member_id}/children")
def add_child_profile(
    member_id: int,
    payload: ChildCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    child = ChildProfile(member_id=member_id, **payload.model_dump())
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@app.get("/api/members/{member_id}/children")
def list_child_profiles(member_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ChildProfile).filter(ChildProfile.member_id == member_id).order_by(ChildProfile.id.desc()).all()


@app.post("/api/card-plans")
def create_card_plan(
    payload: CardPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    plan = CardPlan(**payload.model_dump())
    db.add(plan)
    write_audit_log(db, user.id, "card_plan.create", "card_plan", payload.name, payload.model_dump())
    db.commit()
    db.refresh(plan)
    return plan


@app.get("/api/card-plans")
def list_card_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(CardPlan).order_by(CardPlan.id.asc()).all()


@app.post("/api/member-cards/issue")
def issue_card(
    payload: IssueCardRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN, Role.STORE_ADMIN, Role.EMPLOYEE)),
):
    plan = db.query(CardPlan).filter(CardPlan.id == payload.plan_id).first()
    member = db.query(Member).filter(Member.id == payload.member_id).first()
    if not plan or not member:
        raise HTTPException(status_code=404, detail="卡项或会员不存在")
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE] and payload.purchase_store_id != user.store_id:
        raise HTTPException(status_code=403, detail="只能在本店发卡")

    expires_at = date.today() + timedelta(days=plan.valid_days)
    card = MemberCard(
        member_id=payload.member_id,
        plan_id=payload.plan_id,
        purchase_store_id=payload.purchase_store_id,
        balance_amount=plan.value_amount if plan.plan_type.value == "stored_value" else 0,
        remaining_times=plan.times_total,
        expires_at=expires_at,
    )
    db.add(card)
    db.flush()
    process_referral_after_card_issue(db, card)
    write_audit_log(db, user.id, "member_card.issue", "member_card", str(card.id), payload.model_dump())
    db.commit()
    db.refresh(card)
    return card


@app.get("/api/member-cards")
def list_member_cards(member_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(MemberCard)
    if member_id:
        q = q.filter(MemberCard.member_id == member_id)
    return q.order_by(MemberCard.id.desc()).all()


@app.post("/api/bookings")
def create_booking(payload: BookingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = Booking(created_by_user_id=user.id, **payload.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@app.get("/api/bookings")
def list_bookings(
    store_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Booking)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(Booking.store_id == user.store_id)
    elif store_id:
        q = q.filter(Booking.store_id == store_id)
    return q.order_by(Booking.booking_time.desc()).all()


@app.patch("/api/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE] and booking.store_id != user.store_id:
        raise HTTPException(status_code=403, detail="无权限")
    booking.status = payload.status
    db.commit()
    return booking


@app.post("/api/orders")
def create_order_api(payload: OrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role not in [Role.HQ_ADMIN, Role.STORE_ADMIN, Role.EMPLOYEE]:
        raise HTTPException(status_code=403, detail="无权限")
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE] and payload.store_id != user.store_id:
        raise HTTPException(status_code=403, detail="只能操作本店订单")

    order = create_order(
        db,
        member_id=payload.member_id,
        store_id=payload.store_id,
        employee_id=payload.employee_id,
        payment_method=payload.payment_method,
        items=[row.model_dump() for row in payload.items],
        paid_amount=payload.paid_amount,
        from_douyin_order_id=payload.from_douyin_order_id,
    )

    if payload.from_douyin_order_id:
        dy = db.query(DouyinOrder).filter(DouyinOrder.id == payload.from_douyin_order_id).first()
        if not dy:
            raise HTTPException(status_code=404, detail="抖音订单不存在")
        dy.status = "written_off"
        dy.writeoff_at = datetime.now()
        from app.models import WriteoffRecord

        writeoff = WriteoffRecord(
            douyin_order_id=dy.id,
            order_id=order.id,
            verified_store_id=payload.store_id,
            verified_by_user_id=user.id,
            total_amount=order.paid_amount,
        )
        db.add(writeoff)

    write_audit_log(db, user.id, "order.create", "order", order.order_no, payload.model_dump())
    db.commit()
    db.refresh(order)
    return order


@app.get("/api/orders")
def list_orders(
    store_id: int | None = None,
    member_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Order)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(Order.store_id == user.store_id)
    elif store_id:
        q = q.filter(Order.store_id == store_id)
    if member_id:
        q = q.filter(Order.member_id == member_id)
    return q.order_by(Order.id.desc()).all()


@app.get("/api/orders/{order_id}/items")
def list_order_items(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()


@app.post("/api/douyin/orders")
def create_douyin_order(
    payload: DouyinOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    order = DouyinOrder(
        dy_order_no=payload.dy_order_no,
        member_name=payload.member_name,
        phone_encrypted=encrypt_sensitive(payload.phone),
        amount=payload.amount,
        city=payload.city,
        assigned_store_id=payload.assigned_store_id,
    )
    db.add(order)
    write_audit_log(db, user.id, "douyin_order.create", "douyin_order", payload.dy_order_no, payload.model_dump())
    db.commit()
    db.refresh(order)
    return order


@app.get("/api/douyin/orders")
def list_douyin_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(DouyinOrder)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(DouyinOrder.assigned_store_id == user.store_id)
    rows = q.order_by(DouyinOrder.id.desc()).all()
    return [
        {
            "id": row.id,
            "dy_order_no": row.dy_order_no,
            "member_name": row.member_name,
            "phone": decrypt_sensitive(row.phone_encrypted),
            "amount": row.amount,
            "city": row.city,
            "assigned_store_id": row.assigned_store_id,
            "status": row.status,
            "created_at": row.created_at,
            "writeoff_at": row.writeoff_at,
        }
        for row in rows
    ]


@app.post("/api/douyin/orders/{douyin_order_id}/writeoff")
def writeoff_douyin_order(
    douyin_order_id: int,
    payload: WriteoffRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role not in [Role.HQ_ADMIN, Role.STORE_ADMIN, Role.EMPLOYEE]:
        raise HTTPException(status_code=403, detail="无权限")
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE] and payload.store_id != user.store_id:
        raise HTTPException(status_code=403, detail="只能核销本店")
    dy = db.query(DouyinOrder).filter(DouyinOrder.id == douyin_order_id).first()
    if not dy:
        raise HTTPException(status_code=404, detail="抖音订单不存在")
    if dy.status == "written_off":
        raise HTTPException(status_code=400, detail="抖音订单已核销")

    order = create_order(
        db,
        member_id=payload.member_id,
        store_id=payload.store_id,
        employee_id=payload.employee_id,
        payment_method="douyin",
        items=[{"service_id": payload.service_id, "quantity": 1, "unit_price": dy.amount}],
        paid_amount=dy.amount,
        from_douyin_order_id=dy.id,
    )
    dy.status = "written_off"
    dy.writeoff_at = datetime.now()
    from app.models import WriteoffRecord

    db.add(
        WriteoffRecord(
            douyin_order_id=dy.id,
            order_id=order.id,
            verified_store_id=payload.store_id,
            verified_by_user_id=user.id,
            total_amount=dy.amount,
        )
    )
    write_audit_log(db, user.id, "douyin_order.writeoff", "douyin_order", str(dy.id), payload.model_dump())
    db.commit()
    return {"ok": True, "order_id": order.id}


@app.get("/api/inventory")
def list_inventory(
    store_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(StoreInventory)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(StoreInventory.store_id == user.store_id)
    elif store_id:
        q = q.filter(StoreInventory.store_id == store_id)
    return q.order_by(StoreInventory.id.desc()).all()


@app.post("/api/inventory/adjust")
def adjust_inventory(
    payload: InventoryAdjustRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN, Role.STORE_ADMIN)),
):
    if user.role == Role.STORE_ADMIN and payload.store_id != user.store_id:
        raise HTTPException(status_code=403, detail="只能调整本店库存")
    row = (
        db.query(StoreInventory)
        .filter(
            StoreInventory.store_id == payload.store_id,
            StoreInventory.consumable_id == payload.consumable_id,
        )
        .first()
    )
    if not row:
        row = StoreInventory(
            store_id=payload.store_id,
            consumable_id=payload.consumable_id,
            quantity=0,
            warning_threshold=20,
        )
        db.add(row)
        db.flush()

    row.quantity += payload.change_qty
    db.add(
        InventoryMovement(
            store_id=payload.store_id,
            consumable_id=payload.consumable_id,
            change_qty=payload.change_qty,
            reason=payload.reason,
            operator_id=user.id,
            note=payload.note,
        )
    )
    write_audit_log(db, user.id, "inventory.adjust", "inventory", str(row.id), payload.model_dump())
    db.commit()
    return row


@app.get("/api/inventory/warnings")
def inventory_warnings(
    store_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(StoreInventory).filter(StoreInventory.quantity <= StoreInventory.warning_threshold)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(StoreInventory.store_id == user.store_id)
    elif store_id:
        q = q.filter(StoreInventory.store_id == store_id)
    return q.order_by(StoreInventory.quantity.asc()).all()


@app.get("/api/inventory/movements")
def inventory_movements(
    store_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(InventoryMovement)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(InventoryMovement.store_id == user.store_id)
    elif store_id:
        q = q.filter(InventoryMovement.store_id == store_id)
    return q.order_by(InventoryMovement.id.desc()).limit(200).all()


@app.post("/api/commission-rules")
def create_commission_rule(
    payload: CommissionRuleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN, Role.STORE_ADMIN)),
):
    if user.role == Role.STORE_ADMIN:
        payload.store_id = user.store_id
    row = CommissionRule(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/commission-rules")
def list_commission_rules(
    store_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(CommissionRule)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter((CommissionRule.store_id == user.store_id) | CommissionRule.store_id.is_(None))
    elif store_id is not None:
        q = q.filter((CommissionRule.store_id == store_id) | CommissionRule.store_id.is_(None))
    return q.order_by(CommissionRule.min_amount.asc()).all()


@app.get("/api/payroll")
def list_payroll(
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models import PayrollRecord

    q = db.query(PayrollRecord)
    if month:
        q = q.filter(PayrollRecord.month == month)
    if user.role == Role.EMPLOYEE:
        q = q.filter(PayrollRecord.employee_id == user.id)
    elif user.role == Role.STORE_ADMIN:
        q = q.join(User, PayrollRecord.employee_id == User.id).filter(User.store_id == user.store_id)
    return q.order_by(PayrollRecord.id.desc()).all()


@app.post("/api/reviews")
def create_review(payload: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    review = Review(
        member_id=payload.member_id,
        store_id=payload.store_id,
        order_id=payload.order_id,
        rating=payload.rating,
        content=payload.content,
        images_json=json.dumps(payload.images, ensure_ascii=False),
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@app.get("/api/reviews")
def list_reviews(
    store_id: int | None = None,
    include_deleted: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Review)
    if not include_deleted:
        q = q.filter(Review.is_deleted.is_(False))
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(Review.store_id == user.store_id)
    elif store_id:
        q = q.filter(Review.store_id == store_id)
    rows = q.order_by(Review.is_pinned.desc(), Review.id.desc()).all()
    return [
        {
            "id": row.id,
            "member_id": row.member_id,
            "store_id": row.store_id,
            "order_id": row.order_id,
            "rating": row.rating,
            "content": row.content,
            "images": json.loads(row.images_json or "[]"),
            "reply_content": row.reply_content,
            "is_pinned": row.is_pinned,
            "is_deleted": row.is_deleted,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@app.post("/api/reviews/{review_id}/reply")
def reply_review(
    review_id: int,
    payload: ReviewReply,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN, Role.STORE_ADMIN)),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    if user.role == Role.STORE_ADMIN and review.store_id != user.store_id:
        raise HTTPException(status_code=403, detail="只能回复本店评价")
    review.reply_content = payload.reply_content
    review.reply_by_user_id = user.id
    db.commit()
    return review


@app.post("/api/reviews/{review_id}/moderate")
def moderate_review(
    review_id: int,
    payload: ReviewModeration,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    if payload.is_deleted is not None:
        review.is_deleted = payload.is_deleted
    if payload.is_pinned is not None:
        review.is_pinned = payload.is_pinned
    db.commit()
    return review


@app.get("/api/referrals/records")
def referral_records(
    referrer_member_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(ReferralReward)
    if referrer_member_id:
        q = q.filter(ReferralReward.referrer_member_id == referrer_member_id)
    return q.order_by(ReferralReward.id.desc()).all()


@app.get("/api/referrals/{member_id}/progress")
def referral_progress(member_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    records = db.query(ReferralReward).filter(ReferralReward.referrer_member_id == member_id).all()
    return {
        "member_id": member.id,
        "referral_code": member.referral_code,
        "success_count": member.referral_success_count,
        "target_count": 5,
        "annual_refund_status": member.annual_refund_status,
        "records": [
            {
                "id": r.id,
                "referred_member_id": r.referred_member_id,
                "status": r.status,
                "note": r.note,
                "created_at": r.created_at,
            }
            for r in records
        ],
    }


@app.post("/api/referrals/{member_id}/approve")
def approve_referral(
    member_id: int,
    payload: ReferralApproveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    approve_referral_refund(db, member_id, payload.approve, payload.note)
    write_audit_log(db, user.id, "referral.approve", "member", str(member_id), payload.model_dump())
    db.commit()
    return {"ok": True}


@app.post("/api/settlement/run")
def run_settlement_api(
    payload: SettlementRunRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    target = payload.settlement_date or date.today()
    rows = run_daily_settlement(db, target)
    write_audit_log(db, user.id, "settlement.run", "settlement", target.isoformat(), {"count": len(rows)})
    db.commit()
    return {"ok": True, "count": len(rows), "settlement_date": target}


@app.get("/api/settlement/records")
def settlement_records(
    settlement_date: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(SettlementRecord)
    if settlement_date:
        q = q.filter(SettlementRecord.settlement_date == settlement_date)
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE]:
        q = q.filter(SettlementRecord.store_id == user.store_id)
    return q.order_by(SettlementRecord.id.desc()).all()


@app.get("/api/notifications/{member_id}")
def list_notifications(member_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Notification).filter(Notification.member_id == member_id).order_by(Notification.id.desc()).all()


@app.get("/api/dashboard/store/{store_id}")
def dashboard_store(
    store_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role in [Role.STORE_ADMIN, Role.EMPLOYEE] and user.store_id != store_id:
        raise HTTPException(status_code=403, detail="无权限")

    from app.models import Order, OrderStatus

    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    revenue = (
        db.query(func.sum(Order.paid_amount))
        .filter(Order.store_id == store_id, Order.status == OrderStatus.PAID, Order.created_at >= month_start)
        .scalar()
        or 0
    )
    orders = db.query(func.count(Order.id)).filter(Order.store_id == store_id).scalar() or 0
    members = db.query(func.count(Member.id)).filter(Member.store_id == store_id).scalar() or 0
    warnings = (
        db.query(func.count(StoreInventory.id))
        .filter(StoreInventory.store_id == store_id, StoreInventory.quantity <= StoreInventory.warning_threshold)
        .scalar()
        or 0
    )
    referrals = db.query(func.sum(Member.referral_success_count)).filter(Member.store_id == store_id).scalar() or 0
    reviews_avg = (
        db.query(func.avg(Review.rating)).filter(Review.store_id == store_id, Review.is_deleted.is_(False)).scalar() or 0
    )
    return {
        "store_id": store_id,
        "monthly_revenue": round(float(revenue), 2),
        "order_count": int(orders),
        "member_count": int(members),
        "inventory_warning_count": int(warnings),
        "referral_progress_total": int(referrals),
        "review_avg_rating": round(float(reviews_avg), 2),
    }


@app.get("/api/dashboard/hq")
def dashboard_hq(db: Session = Depends(get_db), user: User = Depends(require_roles(Role.HQ_ADMIN))):
    from app.models import Order, OrderStatus, WriteoffRecord

    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_revenue = (
        db.query(func.sum(Order.paid_amount))
        .filter(Order.status == OrderStatus.PAID, Order.created_at >= month_start)
        .scalar()
        or 0
    )
    douyin_revenue = (
        db.query(func.sum(Order.paid_amount))
        .filter(Order.payment_method == "douyin", Order.created_at >= month_start)
        .scalar()
        or 0
    )
    stores_count = db.query(func.count(Store.id)).scalar() or 0
    members_count = db.query(func.count(Member.id)).scalar() or 0
    reviews_count = db.query(func.count(Review.id)).filter(Review.is_deleted.is_(False)).scalar() or 0
    eligible_rewards = (
        db.query(func.count(Member.id)).filter(Member.annual_refund_status.in_(["eligible", "approved"])).scalar() or 0
    )
    cross_store_writeoff = (
        db.query(func.count(WriteoffRecord.id)).filter(WriteoffRecord.settled.is_(False)).scalar() or 0
    )
    return {
        "monthly_revenue": round(float(total_revenue), 2),
        "monthly_douyin_revenue": round(float(douyin_revenue), 2),
        "stores_count": int(stores_count),
        "members_count": int(members_count),
        "reviews_count": int(reviews_count),
        "eligible_referral_rewards": int(eligible_rewards),
        "pending_cross_store_writeoff": int(cross_store_writeoff),
    }


@app.get("/api/logs")
def audit_logs(
    limit: int = 200,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.HQ_ADMIN)),
):
    from app.models import AuditLog

    rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return rows
