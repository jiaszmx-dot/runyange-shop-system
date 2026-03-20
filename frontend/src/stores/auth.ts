import { defineStore } from "pinia";
import { ref } from "vue";

import api from "../api/http";

export interface AuthUser {
  id: number | null;
  username: string;
  full_name: string;
  role: "hq_admin" | "store_admin" | "employee" | "member";
  store_id: number | null;
}

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("runyangge_token") ?? "");
  const user = ref<AuthUser | null>(null);

  async function login(username: string, password: string) {
    const { data } = await api.post("/auth/login", { username, password });
    token.value = data.access_token;
    localStorage.setItem("runyangge_token", data.access_token);
    const me = await api.get("/auth/me");
    user.value = me.data;
    localStorage.setItem("runyangge_user", JSON.stringify(me.data));
  }

  function restore() {
    const raw = localStorage.getItem("runyangge_user");
    if (raw && !user.value) {
      user.value = JSON.parse(raw);
    }
  }

  function logout() {
    token.value = "";
    user.value = null;
    localStorage.removeItem("runyangge_token");
    localStorage.removeItem("runyangge_user");
  }

  return { token, user, login, restore, logout };
});
