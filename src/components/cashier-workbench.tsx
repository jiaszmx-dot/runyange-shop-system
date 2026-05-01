"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

type CashierItem = {
  id: string;
  name: string;
  category: string;
  type: "服务" | "商品";
  memberPrice: number;
  storePrice: number;
  meta: string;
  flag?: string;
};

type CartItem = CashierItem & {
  quantity: number;
};

type StaffMember = {
  id: string;
  name: string;
  role: string;
  avatar: string;
};

type Promotion = {
  id: string;
  title: string;
  amount: number;
};

const currency = new Intl.NumberFormat("zh-CN", {
  style: "currency",
  currency: "CNY",
  maximumFractionDigits: 0,
});

const sideNav = [
  { key: "cashier", icon: "¥", label: "收银", active: true },
  { key: "member", icon: "VIP", label: "开卡" },
  { key: "topup", icon: "充", label: "充次" },
  { key: "setting", icon: "设", label: "设置" },
  { key: "count", icon: "次", label: "计次" },
  { key: "shift", icon: "班", label: "交班" },
  { key: "order", icon: "单", label: "开单" },
  { key: "list", icon: "订", label: "订单" },
  { key: "more", icon: "…", label: "更多" },
];

const members = [
  {
    id: "m1",
    name: "小米妈妈",
    phone: "139****1288",
    child: "小米",
    tag: "储值会员",
    balance: 1680,
    packages: "小儿推拿 10 次卡",
    vouchers: "常规盒灸券 2 张",
  },
  {
    id: "m2",
    name: "乐乐妈妈",
    phone: "188****2256",
    child: "乐乐",
    tag: "高频回访",
    balance: 320,
    packages: "常规盒灸 4 次",
    vouchers: "暂无项目券",
  },
  {
    id: "m3",
    name: "新客档案",
    phone: "待录入",
    child: "未建档",
    tag: "现场咨询",
    balance: 0,
    packages: "暂无疗程",
    vouchers: "暂无项目券",
  },
];

const staffMembers: StaffMember[] = [
  { id: "s1", name: "张三", role: "店长", avatar: "张" },
  { id: "s2", name: "小唐", role: "收银员", avatar: "唐" },
  { id: "s3", name: "杨小九", role: "理疗师", avatar: "杨" },
];

const paymentMethods = [
  { id: "stored", label: "余额扣费" },
  { id: "gift", label: "赠送次数" },
  { id: "voucher", label: "项目券" },
  { id: "package", label: "次卡/疗程" },
  { id: "wechat", label: "微信收款" },
];

const categories = ["全部", "小儿项目", "成人项目", "特色项目", "商品"];

const items: CashierItem[] = [
  { id: "svc-1", name: "保健推拿", category: "小儿项目", type: "服务", memberPrice: 68, storePrice: 98, meta: "25 分钟" },
  { id: "svc-2", name: "古法脐灸", category: "小儿项目", type: "服务", memberPrice: 68, storePrice: 98, meta: "40 分钟" },
  { id: "svc-3", name: "常规盒灸", category: "小儿项目", type: "服务", memberPrice: 45, storePrice: 60, meta: "40 分钟" },
  { id: "svc-4", name: "推背", category: "成人项目", type: "服务", memberPrice: 98, storePrice: 128, meta: "40 分钟" },
  { id: "svc-5", name: "脏腑", category: "成人项目", type: "服务", memberPrice: 60, storePrice: 80, meta: "40 分钟" },
  { id: "svc-6", name: "肝胆", category: "成人项目", type: "服务", memberPrice: 98, storePrice: 128, meta: "40 分钟" },
  { id: "svc-7", name: "元生灸", category: "特色项目", type: "服务", memberPrice: 198, storePrice: 380, meta: "1 小时", flag: "高客单" },
  { id: "svc-8", name: "督灸", category: "特色项目", type: "服务", memberPrice: 298, storePrice: 398, meta: "60 分钟", flag: "推荐项" },
  { id: "svc-9", name: "通乳", category: "特色项目", type: "服务", memberPrice: 298, storePrice: 398, meta: "60 分钟", flag: "高客单" },
  { id: "prd-1", name: "艾条", category: "商品", type: "商品", memberPrice: 35, storePrice: 39, meta: "库存 20" },
  { id: "prd-2", name: "穴位贴", category: "商品", type: "商品", memberPrice: 20, storePrice: 30, meta: "库存 24" },
  { id: "prd-3", name: "药包", category: "商品", type: "商品", memberPrice: 79, storePrice: 89, meta: "库存 16" },
];

const promotions: Promotion[] = [
  { id: "promo-member", title: "会员价优惠", amount: 45 },
  { id: "promo-recommend", title: "推荐官优惠券", amount: 30 },
];

export function CashierWorkbench() {
  const memberRef = useRef<HTMLDivElement>(null);
  const staffRef = useRef<HTMLElement>(null);
  const staffMenuRef = useRef<HTMLDivElement>(null);
  const paymentRef = useRef<HTMLElement>(null);
  const orderRef = useRef<HTMLElement>(null);
  const promoRef = useRef<HTMLDivElement>(null);

  const [memberKeyword, setMemberKeyword] = useState("");
  const [catalogKeyword, setCatalogKeyword] = useState("");
  const [activeCategory, setActiveCategory] = useState("全部");
  const [selectedMemberId, setSelectedMemberId] = useState("");
  const [selectedStaffId, setSelectedStaffId] = useState("");
  const [selectedPayment, setSelectedPayment] = useState("");
  const [noteEnabled, setNoteEnabled] = useState(false);
  const [note, setNote] = useState("");
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [staffMenuOpen, setStaffMenuOpen] = useState(false);
  const [promoMenuOpen, setPromoMenuOpen] = useState(false);
  const [selectedPromotionIds, setSelectedPromotionIds] = useState<string[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);

  const selectedMember = members.find((entry) => entry.id === selectedMemberId) ?? null;
  const selectedStaff = staffMembers.find((entry) => entry.id === selectedStaffId) ?? null;

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      const target = event.target as Node;

      if (staffMenuOpen && !staffMenuRef.current?.contains(target)) {
        setStaffMenuOpen(false);
      }

      if (promoMenuOpen && !promoRef.current?.contains(target)) {
        setPromoMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, [promoMenuOpen, staffMenuOpen]);

  const visibleMembers = useMemo(() => {
    if (!memberKeyword.trim()) {
      return [];
    }

    const lowerKeyword = memberKeyword.trim().toLowerCase();
    return members.filter((entry) =>
      `${entry.name}${entry.phone}${entry.child}${entry.tag}`.toLowerCase().includes(lowerKeyword),
    );
  }, [memberKeyword]);

  const visibleItems = useMemo(() => {
    return items.filter((entry) => {
      const matchesCategory = activeCategory === "全部" || entry.category === activeCategory;
      const matchesKeyword =
        !catalogKeyword.trim() ||
        `${entry.name}${entry.category}${entry.meta}`.toLowerCase().includes(catalogKeyword.trim().toLowerCase());

      return matchesCategory && matchesKeyword;
    });
  }, [activeCategory, catalogKeyword]);

  const totals = useMemo(() => {
    return cart.reduce(
      (accumulator, entry) => {
        accumulator.count += entry.quantity;
        accumulator.storeTotal += entry.storePrice * entry.quantity;
        accumulator.memberTotal += entry.memberPrice * entry.quantity;
        return accumulator;
      },
      { count: 0, storeTotal: 0, memberTotal: 0 },
    );
  }, [cart]);

  const availablePromotions = useMemo(() => {
    if (!selectedMember || cart.length === 0) {
      return [];
    }

    return promotions;
  }, [selectedMember, cart.length]);

  useEffect(() => {
    setSelectedPromotionIds((current) =>
      current.filter((promotionId) => availablePromotions.some((entry) => entry.id === promotionId)),
    );

    if (availablePromotions.length === 0) {
      setPromoMenuOpen(false);
    }
  }, [availablePromotions]);

  const selectedPromotions = useMemo(
    () => availablePromotions.filter((entry) => selectedPromotionIds.includes(entry.id)),
    [availablePromotions, selectedPromotionIds],
  );

  const discountTotal = useMemo(
    () => selectedPromotions.reduce((sum, entry) => sum + entry.amount, 0),
    [selectedPromotions],
  );

  const actualAmount = Math.max(totals.memberTotal - discountTotal, 0);

  const missingMember = !selectedMember;
  const missingStaff = !selectedStaff;
  const missingPayment = !selectedPayment;
  const missingCart = cart.length === 0;
  const canSubmit = !missingMember && !missingStaff && !missingPayment && !missingCart;

  function addToCart(item: CashierItem) {
    setCart((current) => {
      const existing = current.find((entry) => entry.id === item.id);
      if (!existing) {
        return [...current, { ...item, quantity: 1 }];
      }

      return current.map((entry) =>
        entry.id === item.id ? { ...entry, quantity: entry.quantity + 1 } : entry,
      );
    });
  }

  function updateQuantity(id: string, delta: number) {
    setCart((current) =>
      current
        .map((entry) =>
          entry.id === id ? { ...entry, quantity: Math.max(entry.quantity + delta, 0) } : entry,
        )
        .filter((entry) => entry.quantity > 0),
    );
  }

  function selectMember(memberId: string) {
    const member = members.find((entry) => entry.id === memberId);
    if (!member) {
      return;
    }

    setSelectedMemberId(member.id);
    setMemberKeyword(`${member.name} / ${member.phone}`);
  }

  function resetMemberSelection() {
    setSelectedMemberId("");
    setMemberKeyword("");
    setSelectedPromotionIds([]);
    setPromoMenuOpen(false);
  }

  function handleMemberSearchChange(value: string) {
    if (selectedMemberId) {
      setSelectedMemberId("");
      setSelectedPromotionIds([]);
    }

    setMemberKeyword(value);
  }

  function togglePromotion(promotionId: string) {
    setSelectedPromotionIds((current) =>
      current.includes(promotionId)
        ? current.filter((entry) => entry !== promotionId)
        : [...current, promotionId],
    );
  }

  function toggleNote() {
    setNoteEnabled((current) => {
      if (current) {
        setNote("");
      }

      return !current;
    });
  }

  function handleSubmit() {
    if (canSubmit) {
      return;
    }

    setSubmitAttempted(true);

    if (missingMember) {
      memberRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    if (missingStaff) {
      staffRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    if (missingPayment) {
      paymentRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    if (missingCart) {
      orderRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  return (
    <div className="cashier-workspace">
      <header className="cashier-topbar">
        <div className="cashier-brandbar">
          <div className="cashier-brandmark">
            <span className="cashier-brand-logo">润</span>
            <div>
              <strong>润阳阁云店铺</strong>
              <small>门店经营更轻松</small>
            </div>
          </div>

          <div className="cashier-mode-switch">
            <Link className="cashier-mode-tab active" href="/console/cashier">
              前台收银
            </Link>
            <Link className="cashier-mode-tab" href="/console">
              后台管理
            </Link>
          </div>
        </div>

        <div className="cashier-top-actions">
          <span>润阳阁总店</span>
          <span>收银员：{selectedStaff?.name ?? "未选择"}</span>
          <button className="cashier-header-button" type="button">
            今日交班
          </button>
        </div>
      </header>

      <div className="cashier-app-body">
        <aside className="cashier-side-nav">
          {sideNav.map((item) => (
            <button
              key={item.key}
              className={item.active ? "cashier-side-button active" : "cashier-side-button"}
              type="button"
            >
              <span className="cashier-side-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </aside>

        <section className="cashier-order-pane">
          <div className="cashier-order-header">
            <div className="cashier-order-header-copy">
              <span className="cashier-pane-kicker">会员识别</span>
              <h2>选择会员</h2>
            </div>

            <div
              className={submitAttempted && missingMember ? "cashier-member-control is-error" : "cashier-member-control"}
              ref={memberRef}
            >
              <label className="cashier-search-box" htmlFor="cashier-member-search">
                <input
                  id="cashier-member-search"
                  onChange={(event) => handleMemberSearchChange(event.target.value)}
                  placeholder="搜索会员 / 孩子 / 手机号"
                  type="text"
                  value={memberKeyword}
                />
              </label>
            </div>

            <button className="cashier-primary-ghost" type="button">
              新增会员
            </button>
          </div>

          <div className="cashier-field-stack">
            {!selectedMember && memberKeyword.trim() ? (
              <div className="cashier-member-results">
                {visibleMembers.length > 0 ? (
                  visibleMembers.map((entry) => (
                    <button
                      className="cashier-member-result"
                      key={entry.id}
                      onClick={() => selectMember(entry.id)}
                      type="button"
                    >
                      <strong>{entry.name}</strong>
                      <span>{entry.phone}</span>
                      <small>
                        {entry.tag} · {entry.child}
                      </small>
                    </button>
                  ))
                ) : (
                  <div className="cashier-empty-inline">没有找到会员，可以直接新增会员后再开单。</div>
                )}
              </div>
            ) : null}

            {selectedMember ? (
              <div className="cashier-member-summary">
                <div className="cashier-member-main">
                  <span className="cashier-member-tag">{selectedMember.tag}</span>
                  <h3>{selectedMember.name}</h3>
                  <p>服务对象：{selectedMember.child}</p>
                </div>

                <div className="cashier-balance-box">
                  <strong>{currency.format(selectedMember.balance)}</strong>
                  <span>储值余额</span>
                </div>

                <div className="cashier-member-benefits">
                  <span>{selectedMember.packages}</span>
                  <small>{selectedMember.vouchers}</small>
                  <button className="cashier-inline-link" onClick={resetMemberSelection} type="button">
                    重新选择
                  </button>
                </div>
              </div>
            ) : null}

            {submitAttempted && missingMember ? (
              <p className="cashier-error-text">请先通过搜索选择会员，再继续后续收银流程。</p>
            ) : null}
          </div>

          <div className="cashier-inline-fields">
            <section
              className={submitAttempted && missingStaff ? "cashier-inline-card is-error" : "cashier-inline-card"}
              ref={staffRef}
            >
              <div className="cashier-inline-head">
                <strong>员工选择</strong>
                <span>指定本单服务归属</span>
              </div>

              <div className="cashier-inline-body">
                <div
                  className={staffMenuOpen ? "cashier-staff-picker is-open" : "cashier-staff-picker"}
                  ref={staffMenuRef}
                >
                  <button
                    aria-expanded={staffMenuOpen}
                    className={selectedStaff ? "cashier-staff-trigger has-value" : "cashier-staff-trigger"}
                    onClick={() => setStaffMenuOpen((current) => !current)}
                    type="button"
                  >
                    {selectedStaff ? (
                      <>
                        <span className="cashier-avatar">{selectedStaff.avatar}</span>
                        <span className="cashier-staff-copy">
                          <strong>{selectedStaff.name}</strong>
                          <small>{selectedStaff.role}</small>
                        </span>
                      </>
                    ) : (
                      <span className="cashier-staff-placeholder">请选择员工</span>
                    )}
                    <span className="cashier-chevron">▾</span>
                  </button>

                  {staffMenuOpen ? (
                    <div className="cashier-staff-menu">
                      {staffMembers.map((entry) => (
                        <button
                          className={entry.id === selectedStaffId ? "cashier-staff-option active" : "cashier-staff-option"}
                          key={entry.id}
                          onClick={() => {
                            setSelectedStaffId(entry.id);
                            setStaffMenuOpen(false);
                          }}
                          type="button"
                        >
                          <span className="cashier-avatar">{entry.avatar}</span>
                          <span className="cashier-staff-copy">
                            <strong>{entry.name}</strong>
                            <small>{entry.role}</small>
                          </span>
                        </button>
                      ))}
                    </div>
                  ) : null}
                </div>

                {submitAttempted && missingStaff ? (
                  <p className="cashier-error-text">请先选择本单归属员工。</p>
                ) : null}
              </div>
            </section>

            <section
              className={
                submitAttempted && missingPayment
                  ? "cashier-inline-card stacked is-error"
                  : "cashier-inline-card stacked"
              }
              ref={paymentRef}
            >
              <div className="cashier-inline-head">
                <strong>支付方式</strong>
              </div>

              <div className="cashier-inline-body">
                <label className="cashier-payment-select" htmlFor="cashier-payment-method">
                  <select
                    id="cashier-payment-method"
                    onChange={(event) => setSelectedPayment(event.target.value)}
                    value={selectedPayment}
                  >
                    <option disabled value="">
                      请选择支付方式
                    </option>
                    {paymentMethods.map((entry) => (
                      <option key={entry.id} value={entry.id}>
                        {entry.label}
                      </option>
                    ))}
                  </select>
                  <span className="cashier-select-chevron">▾</span>
                </label>

                {submitAttempted && missingPayment ? (
                  <p className="cashier-error-text">请先选择本单支付或扣费方式。</p>
                ) : null}
              </div>
            </section>
          </div>

          <div className="cashier-order-scroll">
            <section
              className={
                submitAttempted && missingCart
                  ? "cashier-block cashier-order-block is-error"
                  : "cashier-block cashier-order-block"
              }
              ref={orderRef}
            >
              <div className="cashier-block-head">
                <strong>本单项目</strong>
                <span>{cart.length > 0 ? "已选服务与商品" : "请从右侧选择服务或商品"}</span>
              </div>

              {cart.length > 0 ? (
                <div className="cashier-cart-list">
                  {cart.map((entry) => (
                    <article className="cashier-cart-row" key={entry.id}>
                      <div className="cashier-cart-main">
                        <strong>{entry.name}</strong>
                        <span>
                          {entry.type} · {entry.meta}
                        </span>
                      </div>

                      <div className="cashier-cart-stepper">
                        <button onClick={() => updateQuantity(entry.id, -1)} type="button">
                          -
                        </button>
                        <span>{entry.quantity}</span>
                        <button onClick={() => updateQuantity(entry.id, 1)} type="button">
                          +
                        </button>
                      </div>

                      <strong className="cashier-cart-amount">
                        {currency.format(entry.memberPrice * entry.quantity)}
                      </strong>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="cashier-empty-state">右侧点击服务或商品后，这里才会显示本单内容。</div>
              )}

              {submitAttempted && missingCart ? (
                <p className="cashier-error-text">请先添加至少 1 个服务或商品。</p>
              ) : null}
            </section>

            {(selectedPromotions.length > 0 || noteEnabled) ? (
              <section className="cashier-block">
                <div className="cashier-block-head">
                  <strong>优惠与备注</strong>
                  <span>确认本单优惠和特殊说明</span>
                </div>

                {selectedPromotions.length > 0 ? (
                  <div className="cashier-promotion-list">
                    {selectedPromotions.map((entry) => (
                      <div className="cashier-promotion-row" key={entry.id}>
                        <span>{entry.title}</span>
                        <strong>-{currency.format(entry.amount)}</strong>
                      </div>
                    ))}
                  </div>
                ) : null}

                {noteEnabled ? (
                  <textarea
                    className="cashier-note-input"
                    onChange={(event) => setNote(event.target.value)}
                    placeholder="收银备注，例如：孩子今天状态一般，建议下次安排上午时段。"
                    rows={3}
                    value={note}
                  />
                ) : null}
              </section>
            ) : null}
          </div>

          <footer className="cashier-order-footer">
            <div className="cashier-footer-row">
              <span>优惠活动</span>

              <div className="cashier-footer-tools">
                <div className="cashier-promo-picker" ref={promoRef}>
                  <button
                    className={
                      availablePromotions.length > 0
                        ? "cashier-inline-link with-icon cashier-promo-trigger"
                        : "cashier-inline-link with-icon cashier-promo-trigger is-disabled"
                    }
                    onClick={() => {
                      if (availablePromotions.length === 0) {
                        return;
                      }

                      setPromoMenuOpen((current) => !current);
                    }}
                    type="button"
                  >
                    <span>
                      {selectedPromotions.length > 0
                        ? `已选 ${selectedPromotions.length} 项优惠`
                        : availablePromotions.length > 0
                          ? "请选择优惠活动"
                          : "当前暂无可选优惠"}
                    </span>
                    <span className="cashier-inline-arrow">›</span>
                  </button>

                  {promoMenuOpen && availablePromotions.length > 0 ? (
                    <div className="cashier-promo-menu">
                      {availablePromotions.map((entry) => {
                        const active = selectedPromotionIds.includes(entry.id);

                        return (
                          <button
                            className={active ? "cashier-promo-option active" : "cashier-promo-option"}
                            key={entry.id}
                            onClick={() => togglePromotion(entry.id)}
                            type="button"
                          >
                            <span className="cashier-promo-copy">
                              <strong>{entry.title}</strong>
                              <small>优惠 {currency.format(entry.amount)}</small>
                            </span>
                            <span className="cashier-checkmark">{active ? "已选" : "选择"}</span>
                          </button>
                        );
                      })}
                    </div>
                  ) : null}
                </div>

                <button
                  className={noteEnabled ? "cashier-note-toggle active" : "cashier-note-toggle"}
                  onClick={toggleNote}
                  type="button"
                >
                  {noteEnabled ? "已添加备注" : "添加备注"}
                </button>
              </div>
            </div>

            <div className="cashier-footer-totals">
              <div>
                <span>合计数量</span>
                <strong>{totals.count}</strong>
              </div>
              <div>
                <span>本单优惠</span>
                <strong>{currency.format(discountTotal)}</strong>
              </div>
              <div>
                <span>应收金额</span>
                <strong>{currency.format(actualAmount)}</strong>
              </div>
            </div>

            <div className="cashier-footer-actions">
              <button className="cashier-footer-button secondary" type="button">
                取消 [F8]
              </button>
              <button className="cashier-footer-button" type="button">
                挂单
              </button>
              <button
                aria-disabled={!canSubmit}
                className={canSubmit ? "cashier-footer-button primary" : "cashier-footer-button primary is-disabled"}
                onClick={handleSubmit}
                type="button"
              >
                实收 [F5]：{currency.format(actualAmount)}
              </button>
            </div>
          </footer>
        </section>

        <section className="cashier-catalog-pane">
          <div className="cashier-catalog-header">
            <div className="cashier-category-tabs">
              {categories.map((entry) => (
                <button
                  key={entry}
                  className={entry === activeCategory ? "active" : ""}
                  onClick={() => setActiveCategory(entry)}
                  type="button"
                >
                  {entry}
                </button>
              ))}
            </div>

            <button className="cashier-primary-ghost" type="button">
              扫码添加
            </button>
          </div>

          <div className="cashier-product-grid">
            {visibleItems.map((entry) => (
              <button className="cashier-product-card" key={entry.id} onClick={() => addToCart(entry)} type="button">
                <div className="cashier-product-top">
                  <span className={entry.type === "服务" ? "cashier-badge" : "cashier-badge alt"}>
                    {entry.type}
                  </span>
                  {entry.flag ? <small>{entry.flag}</small> : null}
                </div>

                <strong>{entry.name}</strong>
                <p>{entry.meta}</p>

                <div className="cashier-product-price">
                  <span>{currency.format(entry.memberPrice)}</span>
                  <small>门店价 {currency.format(entry.storePrice)}</small>
                </div>
              </button>
            ))}
          </div>

          <div className="cashier-catalog-footer">
            <label className="cashier-code-entry" htmlFor="cashier-code-entry">
              <input
                id="cashier-code-entry"
                onChange={(event) => setCatalogKeyword(event.target.value)}
                placeholder="搜索服务、商品、条码"
                type="text"
                value={catalogKeyword}
              />
            </label>

            <div className="cashier-catalog-actions">
              <button type="button">搜索</button>
              <button type="button">快捷收银 [F6]</button>
              <button type="button">计次项目 [F10]</button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
