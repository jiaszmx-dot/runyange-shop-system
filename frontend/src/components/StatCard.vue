<script setup lang="ts">
defineProps<{
  title: string;
  value: string | number;
  subtitle?: string;
  highlight?: boolean;
}>();
</script>

<template>
  <article class="soft-card card" :class="{ highlight }">
    <p class="title">{{ title }}</p>
    <strong>{{ value }}</strong>
    <small v-if="subtitle">{{ subtitle }}</small>
  </article>
</template>

<style scoped>
.card {
  padding: 16px;
  display: grid;
  gap: 6px;
}

.card.highlight {
  background: linear-gradient(130deg, rgba(137, 203, 198, 0.78), rgba(244, 230, 167, 0.7));
}

.title {
  margin: 0;
  color: #5f6680;
  font-size: 13px;
}

strong {
  font-size: 30px;
}

small {
  color: #5f6680;
}
</style>
