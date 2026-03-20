<script setup lang="ts">
import { onMounted, ref } from "vue";

import api from "../api/http";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const staffList = ref<any[]>([]);
const salaryRows = ref<any[]>([]);
const month = ref("2026-03");
const staffForm = ref({
  username: "",
  password: "123456",
  full_name: "",
  phone: "",
  role: "employee",
  store_id: auth.user?.store_id ?? 2,
  base_salary: 5200,
});

async function load() {
  const [staffRes, salaryRes] = await Promise.all([
    api.get("/users"),
    api.get(`/payroll?month=${month.value}`),
  ]);
  staffList.value = staffRes.data.filter((x: any) => x.role !== "hq_admin");
  salaryRows.value = salaryRes.data;
}

async function createStaff() {
  await api.post("/users", {
    ...staffForm.value,
    role: "employee",
  });
  staffForm.value = {
    username: "",
    password: "123456",
    full_name: "",
    phone: "",
    role: "employee",
    store_id: auth.user?.store_id ?? 2,
    base_salary: 5200,
  };
  await load();
}

onMounted(load);
</script>

<template>
  <div class="staff-page">
    <section class="soft-card panel">
      <h3>员工档案与排班基础</h3>
      <div class="form-grid">
        <input v-model="staffForm.username" placeholder="登录账号" />
        <input v-model="staffForm.full_name" placeholder="员工姓名" />
        <input v-model="staffForm.phone" placeholder="手机号" />
        <input v-model.number="staffForm.base_salary" type="number" placeholder="底薪" />
        <button class="btn btn-primary" @click="createStaff">新增员工</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>姓名</th>
            <th>账号</th>
            <th>角色</th>
            <th>底薪</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="staff in staffList" :key="staff.id">
            <td>{{ staff.full_name }}</td>
            <td>{{ staff.username }}</td>
            <td>{{ staff.role }}</td>
            <td>¥{{ staff.base_salary }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="soft-card panel">
      <div class="salary-head">
        <h3>阶梯提成薪资核算</h3>
        <div class="row">
          <input v-model="month" placeholder="YYYY-MM" />
          <button class="btn btn-primary" @click="load">刷新数据</button>
        </div>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>员工</th>
            <th>月份</th>
            <th>业绩</th>
            <th>提成</th>
            <th>薪资合计</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in salaryRows" :key="`${row.employee_id}-${row.month}`">
            <td>{{ row.employee_id }}</td>
            <td>{{ row.month }}</td>
            <td>-</td>
            <td>¥{{ row.commission }}</td>
            <td><strong>¥{{ row.total_salary }}</strong></td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.staff-page {
  display: grid;
  gap: 14px;
}

.panel {
  padding: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

input {
  border-radius: 10px;
  border: 1px solid rgba(17, 23, 42, 0.15);
  padding: 10px;
}

.salary-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.row {
  display: flex;
  gap: 8px;
}

@media (max-width: 980px) {
  .salary-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
