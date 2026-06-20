<!-- Clean Card Component -->
<template>
  <div class="clean-card" :class="{ 'hoverable': hoverable }">
    <div v-if="$slots.header" class="card-header">
      <slot name="header"></slot>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GlassmorphicCard',
  props: {
    hoverable: { type: Boolean, default: false }
  }
}
</script>

<style scoped>
.clean-card {
  background: var(--cp-bg-card, #fff);
  border: 1px solid var(--cp-border-primary, #E2E8F0);
  border-radius: var(--radius-lg, 16px);
  box-shadow: var(--cp-shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
  transition: all 0.2s ease;
  overflow: hidden;
}

.clean-card.hoverable:hover {
  box-shadow: var(--cp-shadow-md);
  border-color: var(--cp-border-secondary, #CBD5E1);
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--cp-border-primary, #E2E8F0);
  background: var(--cp-bg-card, #fff);
}

.card-body {
  padding: 20px;
}

.card-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--cp-border-primary, #E2E8F0);
  background: var(--cp-bg-secondary, #F1F5F9);
}
</style>
