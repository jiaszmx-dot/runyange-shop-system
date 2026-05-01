"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PropsWithChildren } from "react";

import { consoleNav } from "@/lib/console-nav";

export function ConsoleShell({ children }: PropsWithChildren) {
  const pathname = usePathname();

  if (pathname.startsWith("/console/cashier")) {
    return <div className="cashier-route-shell">{children}</div>;
  }

  return (
    <div className="console-shell">
      <aside className="console-sidebar">
        <div className="console-brand">
          <span className="eyebrow">控制台</span>
          <h1>润阳阁云店铺</h1>
          <p>先把样本店跑顺，再把规则复制到直营连锁与加盟体系。</p>
        </div>

        <div className="console-store-card">
          <span>当前门店</span>
          <strong>润阳阁总店</strong>
          <small>直营样本店 · 今日试运行</small>
        </div>

        <nav className="console-nav">
          {consoleNav.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={active ? "console-link active" : "console-link"}
              >
                <strong>{item.title}</strong>
                <span>{item.description}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="console-content">{children}</div>
    </div>
  );
}
