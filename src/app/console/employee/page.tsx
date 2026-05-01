import { employeeMembers, employeeTimeline, employeeTodos } from "@/lib/console-demo";

export default function EmployeePage() {
  return (
    <div className="console-stack">
      <section className="console-hero">
        <div>
          <span className="eyebrow">员工移动端</span>
          <h2>先看今天做了多少，再看还有谁需要你跟进</h2>
          <p>
            这一页继续按手机优先来设计，信息尽量轻、按钮尽量大、动作尽量短，保证店员在忙的时候也能快速看懂、
            快速点到、快速完成回访和记录。
          </p>
        </div>
      </section>

      <section className="console-section">
        <div className="mobile-preview">
          <div className="phone-frame">
            <div className="phone-top">
              <div>
                <span className="eyebrow">员工视角</span>
                <h3>小唐 · 今日工作</h3>
              </div>
              <strong>周三</strong>
            </div>

            <div className="mobile-metric-grid">
              <article className="mobile-metric-card">
                <span>今日服务人数</span>
                <strong>8</strong>
                <small>比昨日 +2</small>
              </article>
              <article className="mobile-metric-card">
                <span>个人提成</span>
                <strong>¥420</strong>
                <small>含 1 笔充值提成</small>
              </article>
            </div>

            <div className="phone-card">
              <div className="phone-card-head">
                <strong>今日待办</strong>
                <span>轻量优先</span>
              </div>
              <div className="phone-task-list">
                {employeeTodos.map((item) => (
                  <div className="phone-task-row" key={item.title}>
                    <div>
                      <strong>{item.title}</strong>
                      <small>{item.note}</small>
                    </div>
                    <span>{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="phone-card">
              <div className="phone-card-head">
                <strong>服务记录</strong>
                <span>今日时间轴</span>
              </div>
              <div className="phone-timeline">
                {employeeTimeline.map((item) => (
                  <div className="phone-timeline-row" key={`${item.time}-${item.label}`}>
                    <em>{item.time}</em>
                    <div>
                      <strong>{item.label}</strong>
                      <small>{item.member}</small>
                    </div>
                    <span>{item.status}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="phone-card">
              <div className="phone-card-head">
                <strong>我的会员</strong>
                <span>下一步动作</span>
              </div>
              <div className="phone-task-list">
                {employeeMembers.map((member) => (
                  <div className="phone-task-row" key={member.name}>
                    <div>
                      <strong>{member.name}</strong>
                      <small>{member.stage}</small>
                    </div>
                    <span>{member.nextAction}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="phone-tabbar">
              <button className="phone-tab active" type="button">
                今日概览
              </button>
              <button className="phone-tab" type="button">
                回访提醒
              </button>
              <button className="phone-tab" type="button">
                我的会员
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
