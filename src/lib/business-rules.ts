export type RechargePlanRule = {
  name: string;
  rechargeAmount: number;
  memberPriceShared: boolean;
  giftService: string;
  giftTimes: number;
  commissionRate: number;
  note?: string;
};

export type ServiceRule = {
  category: string;
  name: string;
  listPrice: number;
  memberPrice: number;
  pricingUnit: "次" | "小时";
  durationMinutes: number;
  commissionAmount: number;
  consumesInventory: boolean;
  consumableNote?: string;
  enabled: boolean;
};

export type ProductRule = {
  type: "商品" | "耗材";
  name: string;
  category: string;
  listPrice: number;
  memberPrice: number;
  tracksInventory: boolean;
  warningStock: number;
  commissionAmount: number;
  note?: string;
};

export type DeductionRule = {
  serviceName: string;
  allowStoredValue: boolean;
  allowGiftTimes: boolean;
  allowProjectVoucher: boolean;
  allowPackages: boolean;
  packageName?: string;
  note?: string;
};

export type RoleRule = {
  employeeName: string;
  storeName: string;
  role: string;
  canCreateOrder: boolean;
  canRecharge: boolean;
  canRefund: boolean;
  canViewAllMembers: boolean;
};

export type FollowUpRule = {
  triggerScene: string;
  triggerTime: string;
  target: string;
  channel: string;
  messageDirection: string;
  required: boolean;
};

export type PromotionRule = {
  title: string;
  campaignType: "代金券" | "返现奖励";
  benefit: string;
  condition: string;
  validDays: number;
  transferable: boolean;
  fulfillmentMethod: string;
  rewardAmount?: number;
  referralTargetCount?: number;
  qualifyingRechargeAmount?: number;
};

export type FranchisePermissionRule = {
  item: string;
  hqCanView: boolean;
  hqCanEdit: boolean;
  franchiseCanEdit: string;
  note?: string;
};

export type RefundRule = {
  scene: string;
  allowed: boolean;
  operatorRole: string;
  returnBalance: boolean;
  restorePackage: boolean;
  reverseCommission: boolean;
  note?: string;
};

export type DeviceRule = {
  deviceType: string;
  brandOrModel: string;
  connectionMethod: string;
  storeName: string;
  purchased: boolean;
  note?: string;
};

export const rechargePlanRules: RechargePlanRule[] = [
  {
    name: "680 会员",
    rechargeAmount: 688,
    memberPriceShared: true,
    giftService: "常规艾灸",
    giftTimes: 2,
    commissionRate: 5,
    note: "首充/续充都可用",
  },
  {
    name: "1280 会员",
    rechargeAmount: 1288,
    memberPriceShared: true,
    giftService: "常规艾灸",
    giftTimes: 4,
    commissionRate: 8,
    note: "首充/续充都可用",
  },
  {
    name: "2980 会员",
    rechargeAmount: 2980,
    memberPriceShared: true,
    giftService: "常规艾灸",
    giftTimes: 8,
    commissionRate: 10,
    note: "首充/续充都可用",
  },
];

export const serviceRules: ServiceRule[] = [
  { category: "小儿项目", name: "保健推拿", listPrice: 98, memberPrice: 68, pricingUnit: "次", durationMinutes: 25, commissionAmount: 10, consumesInventory: false, enabled: true },
  { category: "小儿项目", name: "古法脐灸", listPrice: 98, memberPrice: 68, pricingUnit: "次", durationMinutes: 40, commissionAmount: 10, consumesInventory: true, enabled: true },
  { category: "小儿项目", name: "常规盒灸", listPrice: 60, memberPrice: 45, pricingUnit: "次", durationMinutes: 40, commissionAmount: 5, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "推背", listPrice: 128, memberPrice: 98, pricingUnit: "次", durationMinutes: 40, commissionAmount: 20, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "脏腑", listPrice: 80, memberPrice: 60, pricingUnit: "次", durationMinutes: 40, commissionAmount: 15, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "肝胆", listPrice: 128, memberPrice: 98, pricingUnit: "次", durationMinutes: 40, commissionAmount: 20, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "常规盒灸", listPrice: 80, memberPrice: 60, pricingUnit: "次", durationMinutes: 40, commissionAmount: 10, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "古法脐灸", listPrice: 128, memberPrice: 98, pricingUnit: "次", durationMinutes: 40, commissionAmount: 20, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "元生灸", listPrice: 380, memberPrice: 198, pricingUnit: "小时", durationMinutes: 60, commissionAmount: 50, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "督灸", listPrice: 398, memberPrice: 298, pricingUnit: "次", durationMinutes: 60, commissionAmount: 20, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "砭法", listPrice: 380, memberPrice: 198, pricingUnit: "小时", durationMinutes: 60, commissionAmount: 50, consumesInventory: true, enabled: true },
  { category: "成人项目", name: "通乳", listPrice: 398, memberPrice: 298, pricingUnit: "次", durationMinutes: 30, commissionAmount: 80, consumesInventory: true, enabled: true },
];

export const productRules: ProductRule[] = [
  { type: "耗材", name: "艾条", category: "耗材", listPrice: 39, memberPrice: 35, tracksInventory: true, warningStock: 20, commissionAmount: 0 },
  { type: "商品", name: "药贴", category: "商品", listPrice: 30, memberPrice: 20, tracksInventory: true, warningStock: 20, commissionAmount: 0 },
  { type: "商品", name: "食疗", category: "商品", listPrice: 80, memberPrice: 68, tracksInventory: true, warningStock: 20, commissionAmount: 0 },
  { type: "商品", name: "药包", category: "商品", listPrice: 89, memberPrice: 79, tracksInventory: true, warningStock: 20, commissionAmount: 0 },
];

export const deductionRules: DeductionRule[] = [
  { serviceName: "保健推拿", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true, packageName: "小儿推拿 10 次卡" },
  { serviceName: "古法脐灸", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true, note: "次卡名称待补充" },
  { serviceName: "常规盒灸", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true, note: "成人/小儿可分别配置次卡" },
  { serviceName: "推背", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true, note: "按项目可做不同疗程包" },
  { serviceName: "脏腑", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true },
  { serviceName: "肝胆", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true },
  { serviceName: "元生灸", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true, note: "小时类项目后续可补充按时长扣减细则" },
  { serviceName: "督灸", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true },
  { serviceName: "砭法", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true, note: "小时类项目后续可补充按时长扣减细则" },
  { serviceName: "通乳", allowStoredValue: true, allowGiftTimes: true, allowProjectVoucher: true, allowPackages: true },
];

export const roleRules: RoleRule[] = [
  { employeeName: "张三", storeName: "总店", role: "店长", canCreateOrder: true, canRecharge: true, canRefund: true, canViewAllMembers: true },
  { employeeName: "李四", storeName: "总店", role: "员工", canCreateOrder: false, canRecharge: false, canRefund: false, canViewAllMembers: false },
  { employeeName: "王麻子", storeName: "总店", role: "员工", canCreateOrder: false, canRecharge: false, canRefund: false, canViewAllMembers: false },
  { employeeName: "小唐", storeName: "总店", role: "收银员", canCreateOrder: true, canRecharge: true, canRefund: true, canViewAllMembers: true },
  { employeeName: "刘小妹", storeName: "总店", role: "总部管理员", canCreateOrder: true, canRecharge: true, canRefund: true, canViewAllMembers: true },
  { employeeName: "杨小小", storeName: "总店", role: "总部运营", canCreateOrder: true, canRecharge: true, canRefund: true, canViewAllMembers: true },
];

export const followUpRules: FollowUpRule[] = [
  { triggerScene: "服务完成后", triggerTime: "1 天后", target: "店员", channel: "微信", messageDirection: "询问恢复情况", required: true },
  { triggerScene: "服务完成后", triggerTime: "客人生日当天", target: "店员", channel: "微信", messageDirection: "生日祝福", required: true },
  { triggerScene: "随时", triggerTime: "1 天后", target: "店员", channel: "微信", messageDirection: "询问恢复情况", required: true },
  { triggerScene: "长时间未来", triggerTime: "30 天后", target: "店员", channel: "微信", messageDirection: "询问身体情况", required: true },
];

export const promotionRules: PromotionRule[] = [
  {
    title: "新客体验券",
    campaignType: "代金券",
    benefit: "30 元代金券",
    condition: "满 98 可用",
    validDays: 15,
    transferable: false,
    fulfillmentMethod: "现场扫码核销",
  },
  {
    title: "推荐官优惠券",
    campaignType: "代金券",
    benefit: "30 元代金券",
    condition: "满 98 可用",
    validDays: 15,
    transferable: false,
    fulfillmentMethod: "现场扫码核销",
  },
  {
    title: "推荐 4 人充值 1980 返现奖励",
    campaignType: "返现奖励",
    benefit: "返现 1980 元",
    condition: "成功推荐 4 人完成 1980 档充值",
    validDays: 365,
    transferable: false,
    fulfillmentMethod: "达标后发起返现处理",
    rewardAmount: 1980,
    referralTargetCount: 4,
    qualifyingRechargeAmount: 1980,
  },
];

export const franchisePermissionRules: FranchisePermissionRule[] = [
  { item: "收银订单", hqCanView: true, hqCanEdit: false, franchiseCanEdit: "是", note: "总部只看数据" },
  { item: "会员充值", hqCanView: true, hqCanEdit: false, franchiseCanEdit: "是", note: "总部只看数据" },
  { item: "项目模板", hqCanView: true, hqCanEdit: true, franchiseCanEdit: "在授权范围内" },
  { item: "价格模板", hqCanView: true, hqCanEdit: true, franchiseCanEdit: "在授权范围内" },
  { item: "活动模板", hqCanView: true, hqCanEdit: true, franchiseCanEdit: "在授权范围内" },
];

export const refundRules: RefundRule[] = [
  { scene: "服务未做退款", allowed: true, operatorRole: "店长", returnBalance: true, restorePackage: true, reverseCommission: true },
];

export const deviceRules: DeviceRule[] = [
  { deviceType: "扫码枪", brandOrModel: "待补充", connectionMethod: "USB", storeName: "总店", purchased: true },
  { deviceType: "热敏打印机", brandOrModel: "待补充", connectionMethod: "USB", storeName: "总店", purchased: true },
  { deviceType: "电脑", brandOrModel: "待补充", connectionMethod: "USB", storeName: "总店", purchased: true },
];

export const businessWarnings = [
  "推荐返现活动已经明确为返现奖励，但第一版还需要定义返现到账方式，是原路退回、现金返现，还是仅登记为待处理返现单。",
  "项目扣减规则已按“全部支持余额、赠送次数、项目券、次卡”录入，但各项目对应的具体次卡名称和扣减细则仍需继续补齐。",
  "收银员退款权限已按你的要求保留，后面我会给退款流程加二次确认和审计日志，降低操作风险。",
];

export const totals = {
  rechargePlans: rechargePlanRules.length,
  services: serviceRules.length,
  products: productRules.length,
  deductionPolicies: deductionRules.length,
  staff: roleRules.length,
  campaigns: promotionRules.length,
};
