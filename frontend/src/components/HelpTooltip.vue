<!-- frontend/src/components/HelpTooltip.vue -->
<template>
  <el-tooltip
    :content="content"
    :placement="placement"
    effect="dark"
    :popper-class="popperClass"
  >
    <span class="help-icon">
      <i class="el-icon-question"></i>
    </span>
  </el-tooltip>
</template>

<script>
export default {
  name: 'HelpTooltip',
  props: {
    content: { type: String, required: true },
    placement: { type: String, default: 'top' },
    popperClass: { type: String, default: 'sci-fi-tooltip' }
  }
}
</script>

<style scoped>
.help-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.2);
  color: var(--cp-neon-blue, #3b82f6);
  cursor: help;
  transition: all 0.3s ease;
}

.help-icon:hover {
  background: rgba(59, 130, 246, 0.4);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}
</style>