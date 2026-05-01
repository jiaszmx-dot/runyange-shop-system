import Link from "next/link";

import { projectProfile } from "@/lib/project";

const previews = [
  {
    title: "老板经营看板",
    href: "/console",
    eyebrow: "老板视角",
    description: "优先看到今日营收、充值金额、到店人数，再往下看趋势、回访与库存预警。",
    points: ["今日营收总览", "充值趋势与到店人数", "待回访会员与库存提醒"],
  },
  {
    title: "收银工作台",
    href: "/console/cashier",
    eyebrow: "收银视角",
    description: "按你确认的流程推进：搜会员、选项目、选员工、选扣费方式、确认优惠、收款、打小票。",
    points: ["适合平板点按", "左订单右选项", "扣费与优惠同屏确认"],
  },
  {
    title: "员工移动端",
    href: "/console/employee",
    eyebrow: "员工视角",
    description: "先看今日服务人数和个人提成，再处理待跟进会员、回访提醒和推荐充值记录。",
    points: ["手机优先布局", "任务轻量清晰", "数据直观不压迫"],
  },
];

export default function Home() {
  return (
    <main className="shell">
      <section className="hero launcher-hero">
        <div className="hero-copy">
          <span className="eyebrow">润阳阁云店铺</span>
          <h1>{projectProfile.name}</h1>
          <p>风格方向已经锁定，现在进入真正的前端样板阶段。先看 3 个最关键的页面，再继续把真实功能接进去。</p>
          <div className="hero-actions">
            <Link className="button primary" href="/console">
              打开老板看板
            </Link>
            <Link className="button secondary" href="/console/cashier">
              打开收银工作台
            </Link>
          </div>
        </div>

        <div className="hero-card">
          <h2>这轮预览重点</h2>
          <ul>
            <li>风格已改为浅灰白底 + 清爽绿色主导，不再混入品牌棕色。</li>
            <li>先把信息架构、交互顺序和可用性锁住，再大规模写功能页。</li>
            <li>所有页面都按“母婴安心感 + 轻奢高级感 + 易用优先”推进。</li>
          </ul>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <span className="eyebrow">样板入口</span>
          <h2>从这里进入你最关心的 3 个页面</h2>
        </div>

        <div className="preview-grid">
          {previews.map((preview) => (
            <article className="preview-card" key={preview.title}>
              <span className="card-kicker">{preview.eyebrow}</span>
              <h3>{preview.title}</h3>
              <p>{preview.description}</p>
              <div className="preview-points">
                {preview.points.map((point) => (
                  <span className="channel-pill" key={point}>
                    {point}
                  </span>
                ))}
              </div>
              <Link className="button primary preview-link" href={preview.href}>
                进入页面
              </Link>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
