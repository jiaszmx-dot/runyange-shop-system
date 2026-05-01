import { followUpRules, promotionRules } from "@/lib/business-rules";

const currency = new Intl.NumberFormat("zh-CN", {
  style: "currency",
  currency: "CNY",
  maximumFractionDigits: 0,
});

export default function GrowthPage() {
  return (
    <div className="console-stack">
      <section className="console-hero">
        <div>
          <span className="eyebrow">增长运营</span>
          <h2>回访提醒、促销活动和推荐返现都放在同一条增长链里</h2>
          <p>
            这一页负责把会员关系真正经营起来。第一版先把规则、触发条件和核销方式跑顺，
            后面再逐步接自动提醒、微信触达和更细的增长报表。
          </p>
        </div>
      </section>

      <section className="console-section">
        <div className="panel-header">
          <span className="eyebrow">回访规则</span>
          <h2>当前已确认的触发逻辑</h2>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>触发场景</th>
                <th>触发时间</th>
                <th>提醒对象</th>
                <th>提醒方式</th>
                <th>文案方向</th>
              </tr>
            </thead>
            <tbody>
              {followUpRules.map((rule) => (
                <tr key={`${rule.triggerScene}-${rule.triggerTime}`}>
                  <td>{rule.triggerScene}</td>
                  <td>{rule.triggerTime}</td>
                  <td>{rule.target}</td>
                  <td>{rule.channel}</td>
                  <td>{rule.messageDirection}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="console-section">
        <div className="panel-header">
          <span className="eyebrow">活动规则</span>
          <h2>促销券与推荐返现模型</h2>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>活动名称</th>
                <th>类型</th>
                <th>权益</th>
                <th>使用条件</th>
                <th>执行方式</th>
              </tr>
            </thead>
            <tbody>
              {promotionRules.map((rule) => (
                <tr key={rule.title}>
                  <td>{rule.title}</td>
                  <td>{rule.campaignType}</td>
                  <td>{rule.benefit}</td>
                  <td>{rule.condition}</td>
                  <td>{rule.fulfillmentMethod}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="console-section">
        <div className="summary-grid">
          {promotionRules
            .filter((rule) => rule.campaignType === "返现奖励")
            .map((rule) => (
              <article className="summary-card" key={rule.title}>
                <h3>{rule.title}</h3>
                <p>达标人数：{rule.referralTargetCount} 人</p>
                <p>充值门槛：{currency.format(rule.qualifyingRechargeAmount ?? 0)}</p>
                <p>返现金额：{currency.format(rule.rewardAmount ?? 0)}</p>
                <p>执行方式：{rule.fulfillmentMethod}</p>
              </article>
            ))}
        </div>
      </section>
    </div>
  );
}
