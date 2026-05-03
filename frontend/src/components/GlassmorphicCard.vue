<!-- frontend/src/components/GlassmorphicCard.vue -->
<template>
  <div class="glassmorphic-card" :class="{ 'glow-active': glowOnHover }">
    <div v-if="$slots.header" class="glass-card-header">
      <slot name="header"></slot>
    </div>
    <div class="glass-card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="glass-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GlassmorphicCard',
  props: {
    glowOnHover: { type: Boolean, default: true }
  }
}
</script>

<style scoped>
.glassmorphic-card {
  background: var(--cp-glass-bg, rgba(255, 255, 255, 0.08));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--cp-glass-border, rgba(255, 255, 255, 0.15));
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(15, 118, 110, 0.15);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.glassmorphic-card.glow-active:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: var(--cp-primary, #0f766e);
  transform: translateY(-6px);
  box-shadow: 0 0 40px rgba(15, 118, 110, 0.4), 0 20px 60px rgba(0, 0, 0, 0.3);
}

.glass-card-header {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.25), rgba(139, 92, 246, 0.15));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 20px;
}

.glass-card-body {
  padding: 20px;
}

.glass-card-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 20px;
  background: rgba(0, 0, 0, 0.2);
}
</style>