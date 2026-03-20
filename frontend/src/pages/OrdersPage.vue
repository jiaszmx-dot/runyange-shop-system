<script setup lang="ts">
import { onMounted, ref } from "vue";

import api from "../api/http";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const members = ref<any[]>([]);
const services = ref<any[]>([]);
const staff = ref<any[]>([]);
const orders = ref<any[]>([]);
const douyinOrders = ref<any[]>([]);

const createForm = ref({
  member_id: 0,
  service_id: 0,
  employee_id: 0,
  store_id: auth.user?.store_id ?? 2,
  payment_method: "wechat",
  quantity: 1,
});

const douyinForm = ref({
  dy_order_no: `DY${Date.now()}`,
  member_name: "抖音新客",
  phone: "13700002222",
  amount: 198,
  city: "上海",
  assigned_store_id: auth.user?.store_id ?? 2,
});

async function loadBase() {
  const [memberRes, serviceRes, staffRes, orderRes, dyRes] = await Promise.all([
    api.get("/members"),
    api.get("/services"),
    api.get("/users"),
    api.get("/orders"),
    api.get("/douyin/orders"),
  ]);
  members.value = memberRes.data;
  services.value = serviceRes.data;
  staff.value = staffRes.data.filter((x: any) => x.role !== "hq_admin");
  orders.value = orderRes.data;
  douyinOrders.value = dyRes.data;
  if (!createForm.value.member_id && members.value.length) {
    createForm.value.member_id = members.value[0].id;
  }
  if (!createForm.value.service_id && services.value.length) {
    createForm.value.service_id = services.value[0].id;
  }
  if (!createForm.value.employee_id && staff.value.length) {
    createForm.value.employee_id = staff.value[0].id;
  }
}

async function createOrder() {
  const service = services.value.find((s) => s.id === createForm.value.service_id);
  await api.post("/orders", {
    member_id: createForm.value.member_id,
    store_id: createForm.value.store_id,
    employee_id: createForm.value.employee_id || null,
    payment_method: createForm.value.payment_method,
    items: [
      {
        service_id: createForm.value.service_id,
        quantity: createForm.value.quantity,
        unit_price: service?.price ?? 0,
      },
    ],
  });
  await loadBase();
}

async function createDouyinOrder() {
  await api.post("/douyin/orders", douyinForm.value);
  douyinForm.value.dy_order_no = `DY${Date.now()}`;
  await loadBase();
}

async function writeoffDy(row: any) {
  await api.post(`/douyin/orders/${row.id}/writeoff`, {
    store_id: auth.user?.store_id ?? createForm.value.store_id,
    employee_id: createForm.value.employee_id || null,
    member_id: createForm.value.member_id,
    service_id: createForm.value.service_id,
  });
  await loadBase();
}

onMounted(loadBase);
</script>

<template>
  <div class="orders-page">
    <section class="soft-card panel">
      <h3>预约开单与现场收银</h3>
      <p class="sub">会员到店后快速开单，自动关联员工绩效与耗材扣减。</p>
      <div class="form-grid">
        <select v-model.number="createForm.member_id">
          <option v-for="member in members" :key="member.id" :value="member.id">{{ member.name }}</option>
        </select>
        <select v-model.number="createForm.service_id">
          <option v-for="service in services" :key="service.id" :value="service.id">{{ service.name }}</option>
        </select>
        <select v-model.number="createForm.employee_id">
          <option v-for="person in staff" :key="person.id" :value="person.id">{{ person.full_name }}</option>
        </select>
        <input v-model.number="createForm.quantity" type="number" min="1" placeholder="数量" />
        <button class="btn btn-primary" @click="createOrder">创建订单</button>
      </div>
    </section>

    <section class="soft-card panel">
      <h3>抖音中央号导单（跨店核销）</h3>
      <div class="form-grid">
        <input v-model="douyinForm.dy_order_no" placeholder="抖音订单号" />
        <input v-model="douyinForm.member_name" placeholder="客户姓名" />
        <input v-model="douyinForm.phone" placeholder="手机号" />
        <input v-model.number="douyinForm.amount" type="number" placeholder="金额" />
        <button class="btn btn-primary" @click="createDouyinOrder">创建抖音订单</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>抖音单号</th>
            <th>客户</th>
            <th>金额</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in douyinOrders" :key="row.id">
            <td>{{ row.dy_order_no }}</td>
            <td>{{ row.member_name }}</td>
            <td>¥{{ row.amount }}</td>
            <td>{{ row.status }}</td>
            <td>
              <button class="btn btn-ghost" :disabled="row.status === 'written_off'" @click="writeoffDy(row)">
                {{ row.status === "written_off" ? "已核销" : "核销到本店" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="soft-card panel">
      <h3>订单列表</h3>
      <table class="table">
        <thead>
          <tr>
            <th>单号</th>
            <th>门店</th>
            <th>员工</th>
            <th>支付方式</th>
            <th>应收</th>
            <th>实收</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>{{ order.order_no }}</td>
            <td>{{ order.store_id }}</td>
            <td>{{ order.employee_id ?? "-" }}</td>
            <td>{{ order.payment_method }}</td>
            <td>¥{{ order.total_amount }}</td>
            <td>¥{{ order.paid_amount }}</td>
            <td>{{ order.status }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.orders-page {
  display: grid;
  gap: 14px;
}

.panel {
  padding: 18px;
}

.sub {
  color: #616b82;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin: 10px 0 12px;
}

input,
select {
  border-radius: 10px;
  border: 1px solid rgba(17, 23, 42, 0.15);
  padding: 10px;
}

@media (max-width: 1150px) {
  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
