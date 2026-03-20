<script setup lang="ts">
import { onMounted, ref } from "vue";

import api from "../api/http";

const reviews = ref<any[]>([]);
const activeReplyId = ref<number | null>(null);
const replyText = ref("");
const pinned = ref(false);
const hide = ref(false);

async function load() {
  const { data } = await api.get("/reviews?include_deleted=true");
  reviews.value = data;
}

function openReply(review: any) {
  activeReplyId.value = review.id;
  replyText.value = review.reply_content ?? "";
  pinned.value = review.is_pinned;
  hide.value = review.is_deleted;
}

async function saveReply() {
  if (!activeReplyId.value) return;
  await api.post(`/reviews/${activeReplyId.value}/reply`, {
    reply_content: replyText.value,
  });
  await api.post(`/reviews/${activeReplyId.value}/moderate`, {
    is_deleted: hide.value,
    is_pinned: pinned.value,
  });
  activeReplyId.value = null;
  await load();
}

onMounted(load);
</script>

<template>
  <div class="reviews-page">
    <section class="soft-card panel">
      <h3>评价中心（总部可置顶/隐藏，门店可回复）</h3>
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>评分</th>
            <th>评价内容</th>
            <th>回复</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="review in reviews" :key="review.id">
            <td>{{ review.id }}</td>
            <td>{{ review.rating }}</td>
            <td>{{ review.content }}</td>
            <td>{{ review.reply_content || "-" }}</td>
            <td>{{ review.is_deleted ? "隐藏" : "公开" }}{{ review.is_pinned ? " / 置顶" : "" }}</td>
            <td>
              <button class="btn btn-ghost" @click="openReply(review)">管理</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-if="activeReplyId" class="soft-card panel">
      <h3>处理评价 #{{ activeReplyId }}</h3>
      <textarea v-model="replyText" rows="4" placeholder="输入回复内容" />
      <div class="row">
        <label><input v-model="pinned" type="checkbox" /> 置顶展示</label>
        <label><input v-model="hide" type="checkbox" /> 隐藏该评价</label>
        <button class="btn btn-primary" @click="saveReply">保存处理结果</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.reviews-page {
  display: grid;
  gap: 14px;
}

.panel {
  padding: 18px;
}

textarea {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(17, 23, 42, 0.15);
  padding: 10px;
  margin-bottom: 10px;
}

.row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

label {
  color: #5f6a82;
  font-size: 14px;
}
</style>
