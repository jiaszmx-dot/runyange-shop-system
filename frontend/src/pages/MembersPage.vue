<script setup lang="ts">
import { onMounted, ref } from "vue";

import api from "../api/http";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const members = ref<any[]>([]);
const stores = ref<any[]>([]);
const loading = ref(false);
const newMember = ref({
  name: "",
  phone: "",
  wechat_openid: "",
  store_id: auth.user?.store_id ?? 2,
  referral_code: "",
});

async function load() {
  loading.value = true;
  try {
    const [memberRes, storeRes] = await Promise.all([api.get("/members"), api.get("/stores")]);
    members.value = memberRes.data;
    stores.value = storeRes.data;
  } finally {
    loading.value = false;
  }
}

async function createMember() {
  await api.post("/members", newMember.value);
  newMember.value = {
    name: "",
    phone: "",
    wechat_openid: "",
    store_id: auth.user?.store_id ?? 2,
    referral_code: "",
  };
  await load();
}

onMounted(load);
</script>

<template>
  <div class="members-page">
    <section class="soft-card panel">
      <h3>新增会员（支持推荐关系绑定）</h3>
      <div class="form-grid">
        <input v-model="newMember.name" placeholder="会员姓名" />
        <input v-model="newMember.phone" placeholder="手机号" />
        <input v-model="newMember.wechat_openid" placeholder="微信 openid" />
        <select v-model.number="newMember.store_id">
          <option v-for="store in stores" :key="store.id" :value="store.id">{{ store.name }}</option>
        </select>
        <input v-model="newMember.referral_code" placeholder="推荐码（可选）" />
      </div>
      <button class="btn btn-primary" @click="createMember">创建会员</button>
    </section>

    <section class="soft-card panel">
      <h3>会员列表</h3>
      <p class="sub">支持 1 位家长绑定多位孩子档案；卡项全国通用；推荐进度可追踪。</p>
      <div v-if="loading">加载中...</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>姓名</th>
            <th>手机号</th>
            <th>门店</th>
            <th>奖励状态</th>
            <th>推荐码</th>
            <th>推荐人</th>
            <th>成功推荐</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in members" :key="member.id">
            <td>{{ member.id }}</td>
            <td>{{ member.name }}</td>
            <td>{{ member.phone }}</td>
            <td>{{ member.store_id }}</td>
            <td>{{ member.annual_refund_status === "pending" ? "未达标" : member.annual_refund_status }}</td>
            <td>{{ member.referral_code }}</td>
            <td>{{ member.referred_by_member_id ?? "-" }}</td>
            <td>{{ member.referral_success_count }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.members-page {
  display: grid;
  gap: 14px;
}

.panel {
  padding: 18px;
}

.panel h3 {
  margin: 0 0 8px;
}

.sub {
  margin: 0 0 14px;
  color: #636d84;
}

.form-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-bottom: 12px;
}

input,
select {
  border-radius: 10px;
  border: 1px solid rgba(17, 23, 42, 0.15);
  padding: 10px;
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
