import { deductionRules, productRules, rechargePlanRules, serviceRules } from "@/lib/business-rules";

const currency = new Intl.NumberFormat("zh-CN", {
  style: "currency",
  currency: "CNY",
  maximumFractionDigits: 0,
});

export default function MasterDataPage() {
  return (
    <div className="console-stack">
      <section className="console-hero">
        <div>
          <span className="eyebrow">基础资料</span>
          <h2>充值、项目、商品和扣减策略都在这里收口</h2>
          <p>
            这些规则决定了开单、扣费、提成和库存如何协同，也是未来多店复制时最不能乱的一层。
            先把标准定清楚，后面每开一家店都会轻很多。
          </p>
        </div>
      </section>

      <section className="console-section">
        <div className="panel-header">
          <span className="eyebrow">充值方案</span>
          <h2>会员充值档位</h2>
        </div>
        <div className="rule-grid">
          {rechargePlanRules.map((plan) => (
            <article className="rule-card" key={plan.name}>
              <span className="card-kicker">{plan.name}</span>
              <h3>{currency.format(plan.rechargeAmount)}</h3>
              <p>
                赠送 {plan.giftService} {plan.giftTimes} 次
              </p>
              <p>充值提成 {plan.commissionRate}%</p>
            </article>
          ))}
        </div>
      </section>

      <section className="console-section">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>分类</th>
                <th>项目名称</th>
                <th>门店价</th>
                <th>会员价</th>
                <th>计价单位</th>
                <th>标准时长</th>
                <th>项目提成</th>
              </tr>
            </thead>
            <tbody>
              {serviceRules.map((service) => (
                <tr key={`${service.category}-${service.name}`}>
                  <td>{service.category}</td>
                  <td>{service.name}</td>
                  <td>{currency.format(service.listPrice)}</td>
                  <td>{currency.format(service.memberPrice)}</td>
                  <td>{service.pricingUnit}</td>
                  <td>{service.durationMinutes} 分钟</td>
                  <td>{currency.format(service.commissionAmount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="console-section">
        <div className="dual-grid">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>类型</th>
                  <th>名称</th>
                  <th>会员价</th>
                  <th>库存预警</th>
                </tr>
              </thead>
              <tbody>
                {productRules.map((product) => (
                  <tr key={product.name}>
                    <td>{product.type}</td>
                    <td>{product.name}</td>
                    <td>{currency.format(product.memberPrice)}</td>
                    <td>{product.warningStock}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>项目</th>
                  <th>余额</th>
                  <th>赠送次数</th>
                  <th>项目券</th>
                  <th>次卡/疗程</th>
                </tr>
              </thead>
              <tbody>
                {deductionRules.map((rule) => (
                  <tr key={rule.serviceName}>
                    <td>{rule.serviceName}</td>
                    <td>{rule.allowStoredValue ? "是" : "否"}</td>
                    <td>{rule.allowGiftTimes ? "是" : "否"}</td>
                    <td>{rule.allowProjectVoucher ? "是" : "否"}</td>
                    <td>{rule.allowPackages ? "是" : "否"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}
