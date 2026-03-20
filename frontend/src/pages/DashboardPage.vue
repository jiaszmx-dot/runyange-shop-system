<script setup lang="ts">
import * as echarts from "echarts";
import { computed, nextTick, onMounted, ref } from "vue";

import api from "../api/http";
import StatCard from "../components/StatCard.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const metrics = ref<Record<string, any>>({});
const trend = ref<{ date: string; revenue: number }[]>([]);
const chartRef = ref<HTMLDivElement | null>(null);

const displayCards = computed(() => {
  if (auth.user?.role === "hq_admin") {
    return [
      { title: "品牌总营收", value: `¥${metrics.value.monthly_revenue ?? 0}`, subtitle: "总部全域实时口径", highlight: true },
      { title: "抖音引流营收", value: `¥${metrics.value.monthly_douyin_revenue ?? 0}`, subtitle: "中央号导单核销" },
      { title: "待结算核销", value: metrics.value.pending_cross_store_writeoff ?? 0, subtitle: "每日24:00自动拆账" },
      { title: "可退费会员", value: metrics.value.eligible_referral_rewards ?? 0, subtitle: "推荐奖励核心池" },
    ];
  }
  return [
    { title: "本店营收", value: `¥${metrics.value.monthly_revenue ?? 0}`, subtitle: "当期汇总", highlight: true },
    { title: "订单量", value: metrics.value.order_count ?? 0, subtitle: "含跨店核销订单" },
    { title: "会员总数", value: metrics.value.member_count ?? 0, subtitle: "含年卡推荐进度" },
    { title: "评价均分", value: metrics.value.review_avg_rating ?? 0, subtitle: "已公开评价" },
  ];
});

function draw() {
  if (!chartRef.value) return;
  const chart = echarts.init(chartRef.value);
  chart.setOption({
    tooltip: { trigger: "axis" },
    grid: { left: 28, right: 16, top: 24, bottom: 22 },
    xAxis: {
      type: "category",
      data: trend.value.map((x) => x.date.slice(5)),
      axisLine: { lineStyle: { color: "#d2d7e4" } },
      axisLabel: { color: "#667086" },
    },
    yAxis: {
      type: "value",
      axisLine: { show: false },
      splitLine: { lineStyle: { color: "#eef1f7" } },
      axisLabel: { color: "#667086" },
    },
    series: [
      {
        type: "line",
        smooth: true,
        data: trend.value.map((x) => x.revenue),
        lineStyle: { width: 3, color: "#6a2b1f" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(113, 47, 24, 0.42)" },
            { offset: 1, color: "rgba(245, 189, 45, 0.05)" },
          ]),
        },
        itemStyle: { color: "#f0bd33" },
      },
    ],
  });
  window.addEventListener("resize", () => chart.resize());
}

async function load() {
  const role = auth.user?.role;
  if (role === "hq_admin") {
    const { data } = await api.get("/dashboard/hq");
    metrics.value = data;
  } else {
    const { data } = await api.get(`/dashboard/store/${auth.user?.store_id}`);
    metrics.value = data;
  }
  const ordersRes = await api.get("/orders");
  const rows = ordersRes.data.slice(0, 120);
  const bucket: Record<string, number> = {};
  rows.forEach((o: any) => {
    const d = String(o.created_at).slice(0, 10);
    bucket[d] = (bucket[d] ?? 0) + Number(o.paid_amount ?? o.total_amount ?? 0);
  });
  trend.value = Object.entries(bucket)
    .map(([date, revenue]) => ({ date, revenue }))
    .slice(-7);
  await nextTick();
  draw();
}

onMounted(load);
</script>

<template>
  <div class="dashboard">
    <section class="hero glass-card">
      <div>
        <p class="chip">经营指挥中心</p>
        <h3>高端连锁运营一屏统览</h3>
        <p class="desc">
          总部统一项目、耗材、结算与推荐规则，门店专注服务交付。系统已接入跨店核销、每日自动分账、阶梯提成与评价可控闭环。
        </p>
      </div>
      <div class="actions">
        <span class="pill">自动结算中台</span>
        <span class="pill">推荐奖励追踪</span>
      </div>
    </section>

    <section class="stats">
      <StatCard
        v-for="card in displayCards"
        :key="card.title"
        :title="card.title"
        :value="card.value"
        :subtitle="card.subtitle"
        :highlight="card.highlight"
      />
    </section>

    <section class="soft-card chart-wrap">
      <header>
        <h4>近7日营收走势</h4>
        <small>用于总部和门店经营复盘</small>
      </header>
      <div ref="chartRef" class="chart" />
    </section>
  </div>
</template>

<style scoped>
.dashboard {
  display: grid;
  gap: 14px;
}

.hero {
  padding: 22px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.chip {
  margin: 0;
  color: #6b7488;
  font-weight: 700;
}

h3 {
  margin: 8px 0;
  font-size: 32px;
}

.desc {
  margin: 0;
  max-width: 780px;
  color: #667086;
}

.actions {
  display: grid;
  gap: 8px;
  align-content: center;
}

.actions .pill {
  background: rgba(20, 31, 54, 0.08);
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.chart-wrap {
  padding: 18px;
}

.chart-wrap header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-wrap h4 {
  margin: 0;
}

.chart-wrap small {
  color: #677088;
}

.chart {
  height: 290px;
  margin-top: 8px;
}

@media (max-width: 1200px) {
  .stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .hero {
    flex-direction: column;
  }
  .stats {
    grid-template-columns: 1fr;
  }
}
</style>
