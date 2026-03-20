import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Role(str, enum.Enum):
    HQ_ADMIN = "hq_admin"
    STORE_ADMIN = "store_admin"
    EMPLOYEE = "employee"
    MEMBER = "member"


class PlanType(str, enum.Enum):
    STORED_VALUE = "stored_value"
    TIMES = "times"
    QUARTER = "quarter"
    ANNUAL = "annual"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELED = "canceled"


class ReferralStatus(str, enum.Enum):
    PENDING = "pending"
    ELIGIBLE = "eligible"
    APPROVED = "approved"
    REFUNDED = "refunded"
    REJECTED = "rejected"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Store(Base, TimestampMixin):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    address: Mapped[str] = mapped_column(String(256), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    is_hq: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hq_take_rate: Mapped[float] = mapped_column(Float, default=0.12, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)

    users = relationship("User", back_populates="store")


class Department(Base, TimestampMixin):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("name", "store_id", name="uq_department_store"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(64), nullable=False)
    nickname_code: Mapped[str] = mapped_column(String(64), default="")
    gender: Mapped[str] = mapped_column(String(16), default="male")
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    phone: Mapped[str] = mapped_column(String(32), default="")
    birthday: Mapped[Optional[date]] = mapped_column(Date)
    address: Mapped[str] = mapped_column(String(255), default="")
    commission_types_json: Mapped[str] = mapped_column(Text, default="[]")
    avatar_url: Mapped[str] = mapped_column(Text, default="")
    bio: Mapped[str] = mapped_column(Text, default="")
    note: Mapped[str] = mapped_column(Text, default="")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"))
    base_salary: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    store = relationship("Store", back_populates="users")


class ServiceItem(Base, TimestampMixin):
    __tablename__ = "service_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    scope: Mapped[str] = mapped_column(String(64), default="child_and_adult")
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    hq_config_locked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Consumable(Base, TimestampMixin):
    __tablename__ = "consumables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    low_threshold: Mapped[float] = mapped_column(Float, default=20, nullable=False)
    global_managed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ServiceConsumableBinding(Base, TimestampMixin):
    __tablename__ = "service_consumable_bindings"
    __table_args__ = (UniqueConstraint("service_id", "consumable_id", name="uq_service_consumable"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service_items.id"), nullable=False)
    consumable_id: Mapped[int] = mapped_column(ForeignKey("consumables.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1, nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class StoreInventory(Base, TimestampMixin):
    __tablename__ = "store_inventory"
    __table_args__ = (UniqueConstraint("store_id", "consumable_id", name="uq_store_consumable"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    consumable_id: Mapped[int] = mapped_column(ForeignKey("consumables.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    warning_threshold: Mapped[float] = mapped_column(Float, default=20, nullable=False)


class InventoryMovement(Base, TimestampMixin):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    consumable_id: Mapped[int] = mapped_column(ForeignKey("consumables.id"), nullable=False)
    change_qty: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(128), nullable=False)
    operator_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str] = mapped_column(String(255), default="")


class Member(Base, TimestampMixin):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    wechat_openid_encrypted: Mapped[str] = mapped_column(String(255), default="")
    phone_encrypted: Mapped[str] = mapped_column(String(255), default="")
    gender: Mapped[str] = mapped_column(String(16), default="unknown")
    birthday: Mapped[Optional[date]] = mapped_column(Date)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"))
    referral_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    referred_by_member_id: Mapped[Optional[int]] = mapped_column(ForeignKey("members.id"))
    referral_success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    annual_refund_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)


class ChildProfile(Base, TimestampMixin):
    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    gender: Mapped[str] = mapped_column(String(16), default="unknown")
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    constitution_note: Mapped[str] = mapped_column(String(255), default="")


class CardPlan(Base, TimestampMixin):
    __tablename__ = "card_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    plan_type: Mapped[PlanType] = mapped_column(Enum(PlanType), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    value_amount: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    times_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_days: Mapped[int] = mapped_column(Integer, default=365, nullable=False)
    nationwide: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    referral_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class MemberCard(Base, TimestampMixin):
    __tablename__ = "member_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey("card_plans.id"), nullable=False)
    purchase_store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    balance_amount: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    remaining_times: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    expires_at: Mapped[Optional[date]] = mapped_column(Date)


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    child_profile_id: Mapped[Optional[int]] = mapped_column(ForeignKey("child_profiles.id"))
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("service_items.id"), nullable=False)
    booking_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    channel: Mapped[str] = mapped_column(String(32), default="mini_program", nullable=False)
    notes: Mapped[str] = mapped_column(String(255), default="")
    created_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PAID, nullable=False)
    from_douyin_order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("douyin_orders.id"))
    is_cross_store: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("service_items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)


class DouyinOrder(Base, TimestampMixin):
    __tablename__ = "douyin_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dy_order_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    member_name: Mapped[str] = mapped_column(String(64), nullable=False)
    phone_encrypted: Mapped[str] = mapped_column(String(255), default="")
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    city: Mapped[str] = mapped_column(String(64), default="")
    assigned_store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"))
    status: Mapped[str] = mapped_column(String(32), default="new", nullable=False)
    writeoff_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class WriteoffRecord(Base, TimestampMixin):
    __tablename__ = "writeoff_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    douyin_order_id: Mapped[int] = mapped_column(ForeignKey("douyin_orders.id"), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    verified_store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    verified_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    hq_amount: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    store_amount: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    settled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    settlement_date: Mapped[Optional[date]] = mapped_column(Date)
    verified_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class SettlementRecord(Base, TimestampMixin):
    __tablename__ = "settlement_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    settlement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    hq_amount: Mapped[float] = mapped_column(Float, nullable=False)
    store_amount: Mapped[float] = mapped_column(Float, nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class CommissionRule(Base, TimestampMixin):
    __tablename__ = "commission_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"))
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    min_amount: Mapped[float] = mapped_column(Float, nullable=False)
    max_amount: Mapped[float] = mapped_column(Float, nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)


class PayrollRecord(Base, TimestampMixin):
    __tablename__ = "payroll_records"
    __table_args__ = (UniqueConstraint("employee_id", "month", name="uq_employee_month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    month: Mapped[str] = mapped_column(String(16), nullable=False)
    base_salary: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    commission: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    total_salary: Mapped[float] = mapped_column(Float, default=0, nullable=False)


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id"))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    images_json: Mapped[str] = mapped_column(Text, default="[]")
    reply_content: Mapped[str] = mapped_column(Text, default="")
    reply_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ReferralReward(Base, TimestampMixin):
    __tablename__ = "referral_rewards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referrer_member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    referred_member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    referred_card_id: Mapped[int] = mapped_column(ForeignKey("member_cards.id"), nullable=False)
    status: Mapped[ReferralStatus] = mapped_column(Enum(ReferralStatus), default=ReferralStatus.PENDING, nullable=False)
    note: Mapped[str] = mapped_column(String(255), default="")
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    msg_type: Mapped[str] = mapped_column(String(32), default="system", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), default="")
    detail_json: Mapped[str] = mapped_column(Text, default="{}")
