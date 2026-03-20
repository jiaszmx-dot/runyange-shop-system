<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

const username = ref("hq_admin");
const password = ref("Admin@123");
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";
  try {
    await auth.login(username.value.trim(), password.value.trim());
    router.push("/dashboard");
  } catch (err: any) {
    error.value = err?.response?.data?.detail ?? "登录失败，请检查账号密码";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="login-card glass-card fade-in">
      <div class="brand">
        <img src="/logo.png" alt="润阳阁LOGO" />
        <div>
          <h1>润阳阁云店铺系统</h1>
          <p>小儿推拿 · 艾灸 · 药浴 · 全国连锁运营平台</p>
        </div>
      </div>
      <div class="tips">
        <span class="pill">演示账号：hq_admin / Admin@123</span>
      </div>
      <form class="form" @submit.prevent="handleLogin">
        <label>
          账号
          <input v-model="username" placeholder="请输入账号" />
        </label>
        <label>
          密码
          <input v-model="password" placeholder="请输入密码" type="password" />
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? "登录中..." : "进入云店铺" }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 20px;
}

.login-card {
  width: min(680px, 100%);
  padding: 26px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand img {
  width: 112px;
  object-fit: contain;
}

.brand h1 {
  margin: 0;
  font-size: 30px;
}

.brand p {
  margin: 8px 0 0;
  color: #5f6680;
}

.tips {
  margin: 18px 0;
}

.pill {
  background: rgba(153, 206, 194, 0.42);
  font-size: 13px;
}

.form {
  display: grid;
  gap: 14px;
}

.form label {
  display: grid;
  gap: 8px;
  font-weight: 600;
}

.form input {
  border: 1px solid rgba(26, 35, 53, 0.16);
  background: rgba(255, 255, 255, 0.75);
  border-radius: 12px;
  padding: 12px;
  font-size: 14px;
}

.error {
  margin: 0;
  color: #d93e55;
}
</style>
