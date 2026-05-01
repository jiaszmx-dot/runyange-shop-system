import {
  dashboardOverview,
  dashboardTasks,
  dashboardTrend,
  memberGrowthFunnel,
  staffRanking,
  storeMatrix,
  topServices,
} from "@/lib/console-demo";

export default function ConsoleHomePage() {
  return (
    <div className="console-stack">
      <section className="console-hero">
        <div>
          <span className="eyebrow">老板看板</span>
          <h2>先看钱、看人、看多店状态，再决定今天盯哪一步</h2>
          <p>
            这一版首页不再像传统 ERP 一样堆满数字，而是先把你每天最需要判断的经营信号放在第一屏，
            让你一打开就知道今天哪家店、哪类会员、哪位员工值得优先关注。
          </p>
        </div>

        <div className="hero-card hero-card-compact">
          <h3>今日经营判断</h3>
          <div className="insight-list">
            <div className="insight-row">
              <strong>总店收银顺畅</strong>
              <span>今天高峰已过，适合安排会员回访。</span>
            </div>
            <div className="insight-row">
              <strong>加盟店总部只读</strong>
              <span>可查看经营情况，但不能代替门店做充值和收银编辑。</span>
            </div>
            <div className="insight-row">
              <strong>返现活动有待处理</strong>
              <span>推荐 4 人充值 1980 的返现规则已进入待核验状态。</span>
            </div>
          </div>
        </div>
      </section>

      <section className="console-section">
        <div className="metric-grid metric-grid-large">
          {dashboardOverview.map((card) => (
            <article className="metric-card" key={card.title}>
              <span>{card.title}</span>
              <strong>{card.value}</strong>
              <div className="metric-foot">
                <em>{card.delta}</em>
                <small>{card.note}</small>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="console-section dashboard-grid">
        <article className="chart-card">
          <div className="panel-header">
            <span className="eyebrow">营收趋势</span>
            <h2>近 7 天门店热度</h2>
          </div>
          <div className="bar-chart">
            {dashboardTrend.map((bar) => (
              <div className="bar-item" key={bar.label}>
                <div className="bar-column">
                  <span style={{ height: `${bar.revenue}%` }} />
                </div>
                <strong>{bar.label}</strong>
                <small>{bar.arrivals} 人</small>
              </div>
            ))}
          </div>
        </article>

        <article className="stack-card">
          <div className="panel-header">
            <span className="eyebrow">今日待办</span>
            <h2>老板今天最该盯的 3 件事</h2>
          </div>
          <div className="stack-list">
            {dashboardTasks.map((task) => (
              <div className="stack-row" key={task.label}>
                <div>
                  <strong>{task.label}</strong>
                  <small>{task.note}</small>
                </div>
                <span>{task.value}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="console-section">
        <div className="panel-header">
          <span className="eyebrow">多店视角</span>
          <h2>直营与加盟都能看，但权限边界要清楚</h2>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>门店</th>
                <th>类型</th>
                <th>今日营收</th>
                <th>充值金额</th>
                <th>到店人数</th>
                <th>总部权限</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {storeMatrix.map((store) => (
                <tr key={store.name}>
                  <td>{store.name}</td>
                  <td>{store.type}</td>
                  <td>{store.revenue}</td>
                  <td>{store.recharge}</td>
                  <td>{store.arrivals}</td>
                  <td>{store.access}</td>
                  <td>{store.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="console-section dashboard-grid">
        <article className="stack-card">
          <div className="panel-header">
            <span className="eyebrow">热门项目</span>
            <h2>今天什么最能打</h2>
          </div>
          <div className="stack-list">
            {topServices.map((service) => (
              <div className="stack-row" key={service.name}>
                <div>
                  <strong>{service.name}</strong>
                  <small>
                    {service.count} · {service.tag}
                  </small>
                </div>
                <span>{service.income}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="stack-card">
          <div className="panel-header">
            <span className="eyebrow">员工排行</span>
            <h2>谁在带动产出</h2>
          </div>
          <div className="stack-list">
            {staffRanking.map((staff) => (
              <div className="stack-row" key={staff.name}>
                <div>
                  <strong>{staff.name}</strong>
                  <small>{staff.note}</small>
                </div>
                <span>{staff.score}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="console-section">
        <div className="panel-header">
          <span className="eyebrow">会员漏斗</span>
          <h2>从到店到充值，再到复购的转化走向</h2>
        </div>
        <div className="funnel-grid">
          {memberGrowthFunnel.map((item, index) => (
            <article className="funnel-card" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <div className="funnel-track">
                <div className="funnel-fill" style={{ width: `${item.percent}%` }} />
              </div>
              <small>{index === 0 ? "基准 100%" : `转化保留 ${item.percent}%`}</small>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
