<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import api from "../api/http";
import { useAuthStore } from "../stores/auth";

type StaffRow = {
  id: number;
  full_name: string;
  gender: string;
  department_name: string;
  store_name: string;
  phone: string;
  birthday: string | null;
  commission_types: string[];
  avatar_url: string;
  bio: string;
};

const auth = useAuthStore();
const loading = ref(false);
const staffList = ref<StaffRow[]>([]);
const salaryRows = ref<any[]>([]);
const stores = ref<any[]>([]);
const departments = ref<any[]>([]);
const month = ref(new Date().toISOString().slice(0, 7));
const keyword = ref("");
const showStaffModal = ref(false);
const avatarInput = ref<HTMLInputElement | null>(null);

const commissionTypeOptions = [
  { value: "card", label: "开卡提成" },
  { value: "recharge", label: "充值提成" },
  { value: "times_recharge", label: "充次提成" },
  { value: "goods_consume", label: "商品消费提成" },
  { value: "fast_consume", label: "快速消费提成" },
  { value: "times_consume", label: "计次消费提成" },
  { value: "hour_consume", label: "计时消费提成" },
  { value: "member_extend", label: "会员延期提成" },
];

const staffNameMap = computed(() =>
  Object.fromEntries(staffList.value.map((row) => [row.id, row.full_name])),
);

const staffForm = ref({
  full_name: "",
  gender: "male",
  nickname_code: "",
  department_id: null as number | string | null,
  store_id: (auth.user?.store_id ?? null) as number | string | null,
  phone: "",
  birthday: "",
  address: "",
  commission_types: [] as string[],
  avatar_url: "",
  bio: "",
  note: "",
});

function resetStaffForm() {
  staffForm.value = {
    full_name: "",
    gender: "male",
    nickname_code: "",
    department_id: null as number | string | null,
    store_id: (auth.user?.store_id ?? stores.value[0]?.id ?? null) as number | string | null,
    phone: "",
    birthday: "",
    address: "",
    commission_types: [],
    avatar_url: "",
    bio: "",
    note: "",
  };
}

async function loadStoresAndDepartments() {
  const [storeRes, deptRes] = await Promise.all([
    api.get("/stores"),
    api.get("/departments"),
  ]);
  stores.value = storeRes.data;
  departments.value = deptRes.data;
  if (!staffForm.value.store_id && stores.value.length > 0) {
    staffForm.value.store_id = stores.value[0].id;
  }
}

async function loadStaff() {
  const query = new URLSearchParams();
  if (keyword.value.trim()) {
    query.set("q", keyword.value.trim());
  }
  const url = query.toString() ? `/users?${query}` : "/users";
  const staffRes = await api.get(url);
  staffList.value = (staffRes.data || []).filter((x: any) => x.role !== "hq_admin");
}

async function loadPayroll() {
  const salaryRes = await api.get(`/payroll?month=${month.value}`);
  salaryRows.value = salaryRes.data || [];
}

async function loadAll() {
  loading.value = true;
  try {
    await Promise.all([loadStoresAndDepartments(), loadStaff(), loadPayroll()]);
  } finally {
    loading.value = false;
  }
}

async function queryStaff() {
  await loadStaff();
}

function openAddStaffModal() {
  resetStaffForm();
  showStaffModal.value = true;
}

function closeAddStaffModal() {
  showStaffModal.value = false;
}

function triggerAvatarUpload() {
  avatarInput.value?.click();
}

function onAvatarSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) {
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    staffForm.value.avatar_url = String(reader.result || "");
  };
  reader.readAsDataURL(file);
}

function toggleCommissionType(value: string) {
  if (staffForm.value.commission_types.includes(value)) {
    staffForm.value.commission_types = staffForm.value.commission_types.filter((item) => item !== value);
  } else {
    staffForm.value.commission_types = [...staffForm.value.commission_types, value];
  }
}

async function addDepartment() {
  const name = window.prompt("请输入新增部门名称");
  if (!name || !name.trim()) {
    return;
  }
  const payload: any = { name: name.trim() };
  if (staffForm.value.store_id) {
    payload.store_id = Number(staffForm.value.store_id);
  }
  const res = await api.post("/departments", payload);
  departments.value.push(res.data);
  staffForm.value.department_id = res.data.id;
}

async function createStaff() {
  const departmentId = staffForm.value.department_id ? Number(staffForm.value.department_id) : null;
  const storeId = staffForm.value.store_id
    ? Number(staffForm.value.store_id)
    : auth.user?.store_id ?? null;

  if (!staffForm.value.full_name.trim()) {
    window.alert("请填写员工姓名");
    return;
  }
  if (!departmentId) {
    window.alert("请选择所属部门");
    return;
  }
  if (staffForm.value.commission_types.length === 0) {
    window.alert("请至少勾选一个提成类型");
    return;
  }

  await api.post("/users", {
    full_name: staffForm.value.full_name.trim(),
    nickname_code: staffForm.value.nickname_code.trim(),
    gender: staffForm.value.gender,
    department_id: departmentId,
    phone: staffForm.value.phone.trim(),
    birthday: staffForm.value.birthday || null,
    address: staffForm.value.address.trim(),
    commission_types: staffForm.value.commission_types,
    avatar_url: staffForm.value.avatar_url,
    bio: staffForm.value.bio.trim(),
    note: staffForm.value.note.trim(),
    role: "employee",
    store_id: storeId,
    base_salary: 0,
  });

  closeAddStaffModal();
  await loadStaff();
}

onMounted(loadAll);
</script>

<template>
  <div class="staff-page">
    <section class="soft-card panel">
      <div class="staff-head">
        <h3>员工绩效与档案管理</h3>
        <div class="toolbar">
          <input v-model="keyword" placeholder="搜索员工（姓名/手机号/编号）" @keyup.enter="queryStaff" />
          <button class="btn btn-ghost" :disabled="loading" @click="queryStaff">查询</button>
          <button class="btn btn-primary" @click="openAddStaffModal">添加员工</button>
        </div>
      </div>

      <table class="table">
        <thead>
          <tr>
            <th>头像</th>
            <th>员工姓名</th>
            <th>性别</th>
            <th>所属部门</th>
            <th>所属店铺</th>
            <th>手机号</th>
            <th>提成类型</th>
            <th>员工生日</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="staff in staffList" :key="staff.id">
            <td>
              <img
                class="avatar-sm"
                :src="staff.avatar_url || '/assets/staff/therapist-a.svg'"
                alt="avatar"
              />
            </td>
            <td>{{ staff.full_name }}</td>
            <td>{{ staff.gender === "female" ? "女士" : "男士" }}</td>
            <td>{{ staff.department_name || "-" }}</td>
            <td>{{ staff.store_name || "-" }}</td>
            <td>{{ staff.phone || "-" }}</td>
            <td>{{ (staff.commission_types || []).join("、") || "-" }}</td>
            <td>{{ staff.birthday || "-" }}</td>
          </tr>
          <tr v-if="staffList.length === 0">
            <td colspan="8" class="empty-cell">暂无员工数据</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="soft-card panel">
      <div class="salary-head">
        <h3>员工绩效核算</h3>
        <div class="row">
          <input v-model="month" placeholder="YYYY-MM" />
          <button class="btn btn-primary" :disabled="loading" @click="loadPayroll">刷新数据</button>
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
            <td>{{ staffNameMap[row.employee_id] || `员工#${row.employee_id}` }}</td>
            <td>{{ row.month }}</td>
            <td>-</td>
            <td>¥{{ row.commission }}</td>
            <td><strong>¥{{ row.total_salary }}</strong></td>
          </tr>
        </tbody>
      </table>
    </section>

    <div v-if="showStaffModal" class="modal-mask" @click.self="closeAddStaffModal">
      <div class="soft-card modal-card">
        <div class="modal-head">
          <h3>添加员工</h3>
          <button class="icon-close" @click="closeAddStaffModal">×</button>
        </div>

        <div class="modal-body">
          <div class="form-left">
            <label class="field">
              <span><em>*</em>员工姓名</span>
              <div class="row">
                <input v-model="staffForm.full_name" placeholder="请输入员工姓名" />
                <select v-model="staffForm.gender">
                  <option value="male">男士</option>
                  <option value="female">女士</option>
                </select>
              </div>
            </label>

            <label class="field">
              <span>昵称/编号</span>
              <input v-model="staffForm.nickname_code" placeholder="请输入昵称或编号" />
            </label>

            <label class="field">
              <span><em>*</em>所属部门</span>
              <div class="row">
                <select v-model="staffForm.department_id">
                  <option :value="null">请选择</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
                </select>
                <button class="btn btn-ghost add-mini" type="button" @click="addDepartment">+</button>
              </div>
            </label>

            <label class="field">
              <span>所属店铺</span>
              <select v-model="staffForm.store_id">
                <option v-for="store in stores" :key="store.id" :value="store.id">{{ store.name }}</option>
              </select>
            </label>

            <label class="field">
              <span>手机号</span>
              <input v-model="staffForm.phone" placeholder="请输入手机号" />
            </label>

            <label class="field">
              <span>员工生日</span>
              <input v-model="staffForm.birthday" type="date" />
            </label>

            <label class="field field-full">
              <span>联系地址</span>
              <input v-model="staffForm.address" placeholder="请输入联系地址" />
            </label>

            <div class="field field-full">
              <span><em>*</em>提成类型</span>
              <div class="commission-grid">
                <label
                  v-for="item in commissionTypeOptions"
                  :key="item.value"
                  class="check-item"
                >
                  <input
                    type="checkbox"
                    :checked="staffForm.commission_types.includes(item.value)"
                    @change="toggleCommissionType(item.value)"
                  />
                  <span>{{ item.label }}</span>
                </label>
              </div>
            </div>

            <label class="field field-full">
              <span>备注</span>
              <textarea v-model="staffForm.note" rows="4" placeholder="请输入备注"></textarea>
            </label>
          </div>

          <div class="form-right">
            <img
              class="avatar-lg"
              :src="staffForm.avatar_url || '/assets/staff/therapist-a.svg'"
              alt="employee-avatar"
            />
            <button class="btn btn-primary upload-btn" type="button" @click="triggerAvatarUpload">
              点击上传图片
            </button>
            <input
              ref="avatarInput"
              type="file"
              accept="image/*"
              class="hidden-file"
              @change="onAvatarSelected"
            />
            <textarea
              v-model="staffForm.bio"
              rows="10"
              placeholder="请输入简介"
            ></textarea>
          </div>
        </div>

        <div class="modal-foot">
          <button class="btn btn-primary" @click="createStaff">保存</button>
          <button class="btn btn-ghost" @click="closeAddStaffModal">关闭</button>
        </div>
      </div>
    </div>
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

.staff-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
}

input,
select,
textarea {
  border-radius: 10px;
  border: 1px solid rgba(17, 23, 42, 0.15);
  padding: 10px;
  font: inherit;
}

.avatar-sm {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  object-fit: cover;
  border: 1px solid rgba(17, 23, 42, 0.1);
}

.empty-cell {
  text-align: center;
  color: #7a8093;
}

.salary-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(15, 17, 25, 0.45);
  display: grid;
  place-items: center;
  padding: 18px;
}

.modal-card {
  width: min(1160px, 98vw);
  max-height: 95vh;
  overflow: auto;
  padding: 0;
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(17, 23, 42, 0.1);
  padding: 12px 18px;
}

.icon-close {
  border: 0;
  background: transparent;
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  display: grid;
  grid-template-columns: 1fr 310px;
  gap: 20px;
  padding: 18px;
}

.form-left {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-content: start;
}

.field {
  display: grid;
  gap: 6px;
}

.field > span {
  font-size: 13px;
  color: #3f4658;
}

.field > span em {
  color: #d94c3d;
  font-style: normal;
  margin-right: 2px;
}

.field-full {
  grid-column: 1 / -1;
}

.add-mini {
  width: 40px;
  padding: 0;
  font-size: 22px;
  line-height: 1;
}

.commission-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px 12px;
  border: 1px dashed rgba(17, 23, 42, 0.2);
  border-radius: 10px;
  padding: 10px 12px;
}

.check-item {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  font-size: 13px;
  color: #2f364a;
}

.form-right {
  display: grid;
  gap: 12px;
  align-content: start;
}

.avatar-lg {
  width: 128px;
  height: 128px;
  border-radius: 999px;
  object-fit: cover;
  border: 3px solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 20px rgba(17, 23, 42, 0.16);
  justify-self: center;
}

.upload-btn {
  justify-self: center;
}

.hidden-file {
  display: none;
}

.modal-foot {
  display: flex;
  gap: 10px;
  justify-content: center;
  border-top: 1px dashed rgba(17, 23, 42, 0.12);
  padding: 14px 18px 18px;
}

@media (max-width: 980px) {
  .staff-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar {
    width: 100%;
    flex-wrap: wrap;
  }

  .toolbar input {
    flex: 1;
    min-width: 220px;
  }

  .salary-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .modal-body {
    grid-template-columns: 1fr;
  }

  .form-left {
    grid-template-columns: 1fr;
  }

  .commission-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
