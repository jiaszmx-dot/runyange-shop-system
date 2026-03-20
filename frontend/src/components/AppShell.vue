<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const navItems = [
  { to: "/dashboard", label: "经营总览" },
  { to: "/members", label: "会员档案" },
  { to: "/orders", label: "预约开单" },
  { to: "/inventory", label: "耗材库存" },
  { to: "/staff", label: "员工绩效" },
  { to: "/reviews", label: "评价中心" },
  { to: "/referrals", label: "推荐奖励" },
];

const roleName = computed(() => {
  const role = auth.user?.role ?? "";
  const roleMap: Record<string, string> = {
    hq_admin: "总部超级管理员",
    store_admin: "加盟店管理员",
    employee: "店员",
    member: "会员",
  };
  return roleMap[role] ?? role;
});

function logout() {
  auth.logout();
  router.push("/login");
}
</script>

<template>
  <div class="shell">
    <aside class="sidebar glass-card fade-in">
      <div class="brand">
        <img src="/logo.png" alt="润阳阁LOGO" />
        <div>
          <h1>润阳阁小儿推拿艾灸馆</h1>
          <p>全国连锁云店铺系统</p>
        </div>
      </div>
      <nav class="nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :class="{ active: route.path === item.to }"
        >
          {{ item.label }}
        </router-link>
      </nav>
      <div class="profile">
        <strong>{{ auth.user?.full_name }}</strong>
        <small>{{ roleName }}</small>
      </div>
    </aside>
    <main class="content">
      <header class="topbar glass-card fade-in">
        <div>
          <h2>{{ route.meta.title ?? "高端门店经营工作台" }}</h2>
          <p>跨店核销 · 自动结算 · 推荐返费 · 阶梯提成 · 总部管控</p>
        </div>
        <button class="btn btn-primary" @click="logout">退出系统</button>
      </header>
      <section class="view fade-in">
        <router-view />
      </section>
    </main>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
  padding: 20px;
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 18px;
}

.sidebar {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.brand {
  display: flex;
  gap: 10px;
  align-items: center;
  border-radius: 16px;
  padding: 8px 8px 12px;
  border-bottom: 1px solid rgba(120, 60, 28, 0.18);
}

.brand img {
  width: 84px;
  height: 84px;
  object-fit: contain;
}

.brand h1 {
  margin: 0;
  font-size: 16px;
  line-height: 1.35;
}

.brand p {
  margin: 4px 0 0;
  font-size: 12px;
  color: #5f6577;
}

.nav {
  display: grid;
  gap: 8px;
}

.nav-item {
  padding: 12px 14px;
  border-radius: 12px;
  text-decoration: none;
  color: #2d3448;
  font-weight: 600;
  transition: 0.2s;
}

.nav-item:hover {
  background: rgba(12, 18, 35, 0.06);
}

.nav-item.active {
  background: linear-gradient(110deg, rgba(126, 49, 26, 0.95), rgba(244, 188, 47, 0.9));
  color: #fff;
}

.profile {
  margin-top: auto;
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid rgba(17, 28, 50, 0.12);
  display: grid;
}

.profile strong {
  font-size: 15px;
}

.profile small {
  color: #646a7f;
}

.content {
  min-width: 0;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 14px;
}

.topbar {
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.topbar h2 {
  margin: 0;
  font-size: 28px;
}

.topbar p {
  margin: 4px 0 0;
  color: #667086;
}

.view {
  min-height: 0;
}

@media (max-width: 1100px) {
  .shell {
    grid-template-columns: 1fr;
  }
  .sidebar {
    width: 100%;
  }
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
