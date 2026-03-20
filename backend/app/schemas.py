from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import BookingStatus, PlanType, ReferralStatus, Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    username: str
    store_id: int | None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str | None = None
    password: str | None = None
    full_name: str
    nickname_code: str = ""
    gender: str = "male"
    department_id: int | None = None
    phone: str = ""
    birthday: date | None = None
    address: str = ""
    commission_types: list[str] = Field(default_factory=list)
    avatar_url: str = ""
    bio: str = ""
    note: str = ""
    role: Role
    store_id: int | None = None
    base_salary: float = 0


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    nickname_code: str
    gender: str
    department_id: int | None
    phone: str
    birthday: date | None
    address: str
    commission_types_json: str
    avatar_url: str
    bio: str
    note: str
    role: Role
    store_id: int | None
    base_salary: float
    is_active: bool


class DepartmentCreate(BaseModel):
    name: str
    store_id: int | None = None
    active: bool = True
    sort_order: int = 0


class StoreCreate(BaseModel):
    code: str
    name: str
    city: str
    address: str = ""
    phone: str = ""
    is_hq: bool = False
    hq_take_rate: float = 0.12


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    city: str
    address: str
    phone: str
    is_hq: bool
    hq_take_rate: float
    status: str


class ServiceCreate(BaseModel):
    name: str
    category: str
    scope: str = "child_and_adult"
    description: str = ""
    price: float
    active: bool = True


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    scope: str
    description: str
    price: float
    active: bool


class ConsumableCreate(BaseModel):
    name: str
    unit: str
    low_threshold: float = 20


class ConsumableBindInput(BaseModel):
    consumable_id: int
    quantity: float = Field(gt=0)
    enabled: bool = True


class MemberCreate(BaseModel):
    name: str
    phone: str = ""
    wechat_openid: str = ""
    gender: str = "unknown"
    birthday: date | None = None
    store_id: int | None = None
    referral_code: str | None = None


class MemberOut(BaseModel):
    id: int
    name: str
    phone: str
    wechat_openid: str
    gender: str
    birthday: date | None
    store_id: int | None
    referral_code: str
    referred_by_member_id: int | None
    referral_success_count: int
    annual_refund_status: str


class ChildCreate(BaseModel):
    name: str
    gender: str = "unknown"
    birth_date: date | None = None
    constitution_note: str = ""


class CardPlanCreate(BaseModel):
    name: str
    plan_type: PlanType
    price: float
    value_amount: float = 0
    times_total: int = 0
    valid_days: int = 365
    nationwide: bool = True
    referral_enabled: bool = False


class IssueCardRequest(BaseModel):
    member_id: int
    plan_id: int
    purchase_store_id: int


class BookingCreate(BaseModel):
    member_id: int
    child_profile_id: int | None = None
    store_id: int
    service_id: int
    booking_time: datetime
    channel: str = "mini_program"
    notes: str = ""


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class OrderItemIn(BaseModel):
    service_id: int
    quantity: int = Field(default=1, gt=0)
    unit_price: float | None = None


class OrderCreate(BaseModel):
    member_id: int
    store_id: int
    employee_id: int | None = None
    payment_method: str = "wechat"
    paid_amount: float | None = None
    from_douyin_order_id: int | None = None
    items: list[OrderItemIn]


class DouyinOrderCreate(BaseModel):
    dy_order_no: str
    member_name: str
    phone: str = ""
    amount: float
    city: str = ""
    assigned_store_id: int | None = None


class WriteoffRequest(BaseModel):
    store_id: int
    employee_id: int | None = None
    member_id: int
    service_id: int


class InventoryAdjustRequest(BaseModel):
    store_id: int
    consumable_id: int
    change_qty: float
    reason: str
    note: str = ""


class CommissionRuleCreate(BaseModel):
    store_id: int | None = None
    name: str
    min_amount: float
    max_amount: float
    rate: float


class ReviewCreate(BaseModel):
    member_id: int
    store_id: int
    order_id: int | None = None
    rating: int = Field(ge=1, le=5)
    content: str = ""
    images: list[str] = []


class ReviewReply(BaseModel):
    reply_content: str


class ReviewModeration(BaseModel):
    is_deleted: bool | None = None
    is_pinned: bool | None = None


class SettlementRunRequest(BaseModel):
    settlement_date: date | None = None


class ReferralApproveRequest(BaseModel):
    approve: bool = True
    note: str = ""


class ReferralRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    referrer_member_id: int
    referred_member_id: int
    referred_card_id: int
    status: ReferralStatus
    note: str
