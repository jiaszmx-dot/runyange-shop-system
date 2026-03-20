<script setup lang="ts">
import { onMounted, ref } from "vue";

import api from "../api/http";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const materials = ref<any[]>([]);
const inventoryWarnings = ref<any[]>([]);
const tiers = ref<any[]>([]);
const newMaterial = ref({
  name: "",
  unit: "piece",
  low_threshold: 20,
});

async function load() {
  const [materialsRes, warningRes, tierRes] = await Promise.all([
    api.get("/consumables"),
    api.get(`/inventory/warnings?store_id=${auth.user?.store_id ?? 2}`),
    api.get(`/commission-rules?store_id=${auth.user?.store_id ?? 2}`),
  ]);
  materials.value = materialsRes.data;
  inventoryWarnings.value = warningRes.data;
  tiers.value = tierRes.data;
}

async function createMaterial() {
  await api.post("/consumables", newMaterial.value);
  newMaterial.value = { name: "", unit: "piece", low_threshold: 20 };
  await load();
}

onMounted(load);
</script>

<template>
  <div class="inventory-page">
    <section class="soft-card panel">
      <h3>耗材库存（总部强管控）</h3>
      <p class="sub">服务结算自动扣减库存，低于预警线时自动标红提醒。</p>
      <table class="table">
        <thead>
          <tr>
            <th>耗材</th>
            <th>单位</th>
            <th>库存</th>
            <th>预警值</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in materials" :key="m.id">
            <td>{{ m.name }}</td>
            <td>{{ m.unit }}</td>
            <td>-</td>
            <td>{{ m.low_threshold }}</td>
            <td>
              <span class="pill">总部标准耗材</span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="soft-card panel">
      <h3>新增耗材（总部）</h3>
      <div class="form-grid">
        <input v-model="newMaterial.name" placeholder="名称" />
        <input v-model="newMaterial.unit" placeholder="单位" />
        <input v-model.number="newMaterial.low_threshold" type="number" placeholder="预警值" />
        <button class="btn btn-primary" @click="createMaterial">新增耗材</button>
      </div>
    </section>

    <section class="soft-card panel">
      <h3>本店库存预警</h3>
      <table class="table">
        <thead>
          <tr>
            <th>库存记录ID</th>
            <th>耗材ID</th>
            <th>当前库存</th>
            <th>预警值</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in inventoryWarnings" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.consumable_id }}</td>
            <td>{{ item.quantity }}</td>
            <td>{{ item.warning_threshold }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="soft-card panel">
      <h3>阶梯提成模板</h3>
      <table class="table">
        <thead>
          <tr>
            <th>业绩区间</th>
            <th>提成比例</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tier in tiers" :key="tier.id">
            <td>{{ tier.min_amount }} - {{ tier.max_amount ?? "以上" }}</td>
            <td>{{ Math.round(tier.rate * 100) }}%</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.inventory-page {
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
}

input {
  border-radius: 10px;
  border: 1px solid rgba(17, 23, 42, 0.15);
  padding: 10px;
}

.pill {
  font-size: 12px;
  padding: 3px 10px;
  background: rgba(144, 210, 223, 0.38);
}

.danger {
  background: rgba(217, 62, 85, 0.18);
  color: #9e2237;
}

@media (max-width: 980px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
