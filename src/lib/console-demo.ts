export const dashboardOverview = [
  {
    title: "今日营收",
    value: "¥4,860",
    delta: "+12.6%",
    note: "比昨日多 ¥546",
  },
  {
    title: "充值金额",
    value: "¥2,980",
    delta: "+1 单",
    note: "2980 会员档今天已成交",
  },
  {
    title: "到店人数",
    value: "18",
    delta: "+3",
    note: "小儿项目占比 56%",
  },
  {
    title: "待回访会员",
    value: "12",
    delta: "3 位新客",
    note: "今天需要安排首访和疗后回访",
  },
];

export const dashboardTrend = [
  { label: "周一", revenue: 62, arrivals: 9 },
  { label: "周二", revenue: 48, arrivals: 7 },
  { label: "周三", revenue: 71, arrivals: 12 },
  { label: "周四", revenue: 66, arrivals: 10 },
  { label: "周五", revenue: 84, arrivals: 16 },
  { label: "周六", revenue: 92, arrivals: 18 },
  { label: "周日", revenue: 75, arrivals: 14 },
];

export const dashboardTasks = [
  {
    label: "待回访会员",
    value: "12",
    note: "3 位新客今天需要首次关怀，2 位昨日治疗后需跟进恢复情况。",
  },
  {
    label: "库存预警",
    value: "2",
    note: "艾条与穴位贴都低于安全库存，建议今天补录采购单。",
  },
  {
    label: "返现待处理",
    value: "1",
    note: "1 位会员已达成推荐 4 人充值 1980 的返现条件。",
  },
];

export const topServices = [
  { name: "保健推拿", count: "今日 8 单", income: "¥544", tag: "小儿核心" },
  { name: "常规盒灸", count: "今日 5 单", income: "¥285", tag: "高复购" },
  { name: "通乳", count: "今日 2 单", income: "¥596", tag: "高客单" },
];

export const staffRanking = [
  { name: "张三", score: "¥680", note: "服务提成 + 充值提成双领先" },
  { name: "小唐", score: "¥420", note: "收银转化率稳定，充值解释能力强" },
  { name: "杨小九", score: "¥260", note: "今日回访带回 3 位老会员复购" },
];

export const storeMatrix = [
  {
    name: "润阳阁总店",
    type: "直营样本店",
    revenue: "¥4,860",
    recharge: "¥2,980",
    arrivals: 18,
    access: "可编辑",
    status: "运行顺畅",
  },
  {
    name: "润阳阁松岗店",
    type: "加盟试运行",
    revenue: "¥3,220",
    recharge: "¥1,980",
    arrivals: 11,
    access: "总部只读",
    status: "库存盘点延迟",
  },
  {
    name: "润阳阁宝安店",
    type: "直营筹备店",
    revenue: "未开业",
    recharge: "-",
    arrivals: 0,
    access: "可编辑",
    status: "基础资料待导入",
  },
];

export const memberGrowthFunnel = [
  { label: "到店咨询", value: 26, percent: 100 },
  { label: "首次开单", value: 18, percent: 69 },
  { label: "充值成为会员", value: 7, percent: 27 },
  { label: "30 天内复购", value: 4, percent: 15 },
];

export const cashierMembers = [
  {
    id: "m1",
    name: "小米妈妈",
    phone: "139****1288",
    tag: "储值会员",
    balance: 1680,
    packageSummary: "小儿推拿 10 次卡",
    vouchers: "常规盒灸券 2 张",
    childName: "小米",
  },
  {
    id: "m2",
    name: "乐乐妈妈",
    phone: "188****2256",
    tag: "高频回访",
    balance: 320,
    packageSummary: "常规盒灸 4 次",
    vouchers: "无项目券",
    childName: "乐乐",
  },
  {
    id: "m3",
    name: "新客档案",
    phone: "待录入",
    tag: "现场咨询",
    balance: 0,
    packageSummary: "暂无疗程",
    vouchers: "无项目券",
    childName: "未建档",
  },
];

export const orderSources = ["会员到店", "到店咨询", "到店充值"];

export const paymentMethods = [
  { id: "stored", label: "余额扣费" },
  { id: "gift", label: "赠送次数" },
  { id: "voucher", label: "项目券" },
  { id: "package", label: "次卡/疗程包" },
  { id: "wechat", label: "微信收款" },
];

export const cashierPromotions = [
  "会员价已生效",
  "推荐官优惠券 -¥30",
  "小儿项目组合减免 -¥20",
];

export const cashierFollowUps = [
  { title: "服务后 1 天回访", due: "明天 10:00", owner: "小唐" },
  { title: "新客建档补全", due: "今日收银后", owner: "前台" },
  { title: "推荐返现资格核验", due: "今晚闭店前", owner: "店长" },
];

export const employeeTodos = [
  {
    title: "待跟进会员",
    value: "6",
    note: "3 位小儿项目家长今天需要回访，重点问睡眠和食欲变化。",
  },
  {
    title: "回访提醒",
    value: "4",
    note: "1 位生日关怀，3 位疗后回访。",
  },
  {
    title: "推荐充值记录",
    value: "2",
    note: "其中 1 位会员已接近返现达标。",
  },
];

export const employeeTimeline = [
  { time: "09:30", label: "保健推拿", member: "小米妈妈", status: "已完成" },
  { time: "11:00", label: "常规盒灸", member: "乐乐妈妈", status: "已完成" },
  { time: "14:00", label: "通乳", member: "李女士", status: "进行中" },
];

export const employeeMembers = [
  { name: "小米妈妈", stage: "疗后 1 天", nextAction: "明天上午回访" },
  { name: "乐乐妈妈", stage: "7 天复购提醒", nextAction: "推送常规盒灸券" },
  { name: "王女士", stage: "推荐官跟进", nextAction: "确认第 3 位充值进度" },
];
