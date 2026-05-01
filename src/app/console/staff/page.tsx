import { franchisePermissionRules, refundRules, roleRules } from "@/lib/business-rules";

export default function StaffPage() {
  return (
    <div className="console-stack">
      <section className="console-hero">
        <div>
          <span className="eyebrow">权限风控</span>
          <h2>员工角色、加盟权限和退款边界要先钉死</h2>
          <p>
            这块越早定清楚，后面越不容易因为权限过宽、加盟越权或退款误操作而返工。
            你已经明确“直营可全权编辑、加盟总部只看不代操作”的原则，这页就是把它产品化。
          </p>
        </div>
      </section>

      <section className="console-section">
        <div className="dual-grid">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>员工</th>
                  <th>角色</th>
                  <th>开单</th>
                  <th>充值</th>
                  <th>退款</th>
                  <th>查看全部会员</th>
                </tr>
              </thead>
              <tbody>
                {roleRules.map((role) => (
                  <tr key={`${role.storeName}-${role.employeeName}`}>
                    <td>{role.employeeName}</td>
                    <td>{role.role}</td>
                    <td>{role.canCreateOrder ? "是" : "否"}</td>
                    <td>{role.canRecharge ? "是" : "否"}</td>
                    <td>{role.canRefund ? "是" : "否"}</td>
                    <td>{role.canViewAllMembers ? "是" : "否"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>加盟项</th>
                  <th>总部查看</th>
                  <th>总部编辑</th>
                  <th>加盟店编辑</th>
                </tr>
              </thead>
              <tbody>
                {franchisePermissionRules.map((rule) => (
                  <tr key={rule.item}>
                    <td>{rule.item}</td>
                    <td>{rule.hqCanView ? "是" : "否"}</td>
                    <td>{rule.hqCanEdit ? "是" : "否"}</td>
                    <td>{rule.franchiseCanEdit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="console-section">
        <div className="summary-grid">
          {refundRules.map((rule) => (
            <article className="summary-card" key={rule.scene}>
              <h3>{rule.scene}</h3>
              <p>操作角色：{rule.operatorRole}</p>
              <p>恢复余额：{rule.returnBalance ? "是" : "否"}</p>
              <p>恢复次卡：{rule.restorePackage ? "是" : "否"}</p>
              <p>反结算提成：{rule.reverseCommission ? "是" : "否"}</p>
            </article>
          ))}

          <article className="summary-card">
            <h3>下一步风控</h3>
            <p>退款流程后续会加二次确认、操作日志、退款原因和门店负责人复核，降低误操作风险。</p>
          </article>
        </div>
      </section>
    </div>
  );
}
