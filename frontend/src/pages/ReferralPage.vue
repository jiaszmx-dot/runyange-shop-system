<script setup lang="ts">
import { onMounted, ref } from "vue";

import api from "../api/http";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const referralMembers = ref<any[]>([]);
const progressMap = ref<Record<number, any>>({});

async function load() {
  const { data } = await api.get("/members");
  referralMembers.value = data.filter((x: any) => x.referral_code);
  const all = await Promise.all(
    referralMembers.value.map((member: any) => api.get(`/referrals/${member.id}/progress`)),
  );
  progressMap.value = {};
  referralMembers.value.forEach((member: any, i: number) => {
    progressMap.value[member.id] = all[i].data;
  });
}

async function approve(memberId: number) {
  await api.post(`/referrals/${memberId}/approve`, { approve: true, note: "" });
  await load();
}

onMounted(load);
</script>

<template>
  <div class="ref-page">
    <section class="soft-card panel">
      <h3>1980年卡推荐奖励中心</h3>
      <p class="sub">年卡会员成功推荐 5 名新客办理同档年卡后，可退还年费并继续享受当年服务（总部审核）。</p>
      <table class="table">
        <thead>
          <tr>
            <th>会员ID</th>
            <th>姓名</th>
            <th>推荐码</th>
            <th>进度</th>
            <th>退费资格</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in referralMembers" :key="member.id">
            <td>{{ member.id }}</td>
            <td>{{ member.name }}</td>
            <td>{{ member.referral_code }}</td>
            <td>
              {{ progressMap[member.id]?.success_count ?? 0 }}/{{ progressMap[member.id]?.target_count ?? 5 }}
            </td>
            <td>
              {{
                member.annual_refund_status === "approved"
                  ? "已审核通过"
                  : member.annual_refund_status === "eligible"
                    ? "可审核"
                    : "待达标"
              }}
            </td>
            <td>
              <button v-if="auth.user?.role === 'hq_admin'" class="btn btn-primary" @click="approve(member.id)">
                审核退费
              </button>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.ref-page {
  display: grid;
}

.panel {
  padding: 18px;
}

.sub {
  color: #606a81;
}
</style>
