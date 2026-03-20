import { createRouter, createWebHistory } from "vue-router";

import AppShell from "./components/AppShell.vue";
import DashboardPage from "./pages/DashboardPage.vue";
import InventoryPage from "./pages/InventoryPage.vue";
import LoginPage from "./pages/LoginPage.vue";
import MembersPage from "./pages/MembersPage.vue";
import OrdersPage from "./pages/OrdersPage.vue";
import ReferralPage from "./pages/ReferralPage.vue";
import ReviewsPage from "./pages/ReviewsPage.vue";
import StaffPage from "./pages/StaffPage.vue";
import { useAuthStore } from "./stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: LoginPage },
    {
      path: "/",
      component: AppShell,
      children: [
        { path: "", redirect: "/dashboard" },
        { path: "dashboard", component: DashboardPage },
        { path: "members", component: MembersPage },
        { path: "orders", component: OrdersPage },
        { path: "inventory", component: InventoryPage },
        { path: "staff", component: StaffPage },
        { path: "reviews", component: ReviewsPage },
        { path: "referrals", component: ReferralPage },
      ],
    },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.path !== "/login" && !auth.token) {
    return "/login";
  }
  if (to.path === "/login" && auth.token) {
    return "/dashboard";
  }
  return true;
});

export default router;
