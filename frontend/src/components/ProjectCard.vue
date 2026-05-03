<template>
  <div class="project-card" :class="{ 'active': selected }">
    <div class="card-header">
      <div class="project-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
        </svg>
      </div>
      <div class="project-info">
        <h3 class="project-name">{{ project.name }}</h3>
        <p class="project-url">{{ project.repo_url }}</p>
      </div>
      <div class="status-badge" :class="project.status">
        {{ statusText }}
      </div>
    </div>

    <div class="card-body">
      <ProgressBar v-if="project.status === 'analyzing'" :progress="project.progress" :message="progressMessage"
        :status="project.status" />

      <div v-else-if="project.status === 'completed'" class="completed-info">
        <p class="completed-text">分析完成于 {{ formatDate(project.last_analyzed_at) }}</p>
      </div>

      <div v-else-if="project.status === 'failed'" class="failed-info">
        <p class="failed-text">分析失败，请重试</p>
      </div>
    </div>

    <div class="card-actions">
      <button v-if="project.status === 'pending'" class="btn btn-primary" @click="$emit('analyze', project.id)">
        开始分析
      </button>
      <template v-else-if="project.status === 'analyzing'">
        <button class="btn btn-warning" @click="$emit('cancel', project.id)">
          取消分析
        </button>
      </template>
      <template v-else-if="project.status === 'completed'">
        <button class="btn btn-success" @click="$emit('view-report', project.id)">
          查看报告
        </button>
        <button class="btn btn-info" @click="$emit('qa', project.id)">
          交互式问答
        </button>
      </template>
      <button v-else-if="project.status === 'failed'" class="btn btn-warning" @click="$emit('retry', project.id)">
        重试分析
      </button>
      <button v-if="project.status !== 'analyzing'" class="btn btn-danger" @click="$emit('delete', project.id)">
        删除
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ProgressBar from './ProgressBar.vue'

const props = defineProps({
  project: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  },
  progressMessage: {
    type: String,
    default: ''
  }
})

defineEmits(['analyze', 'cancel', 'view-report', 'delete', 'retry'])

const statusText = computed(() => {
  const statusMap = {
    pending: '待分析',
    analyzing: '分析中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[props.project.status] || '未知'
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.project-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.project-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
}

.project-card.active {
  border-color: #667eea;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.project-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.project-icon svg {
  width: 24px;
  height: 24px;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-url {
  font-size: 13px;
  color: #a0aec0;
  margin: 4px 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.status-badge.analyzing {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
}

.status-badge.completed {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.status-badge.failed {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.card-body {
  margin-bottom: 16px;
}

.completed-info,
.failed-info {
  padding: 12px;
  border-radius: 8px;
}

.completed-info {
  background: rgba(40, 167, 69, 0.1);
}

.failed-info {
  background: rgba(220, 53, 69, 0.1);
}

.completed-text,
.failed-text {
  margin: 0;
  font-size: 14px;
}

.completed-text {
  color: #28a745;
}

.failed-text {
  color: #dc3545;
}

.card-actions {
  display: flex;
  gap: 10px;
}

.btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-success {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
  border: 1px solid rgba(40, 167, 69, 0.3);
}

.btn-success:hover {
  background: rgba(40, 167, 69, 0.3);
}

.btn-info {
  background: rgba(13, 110, 253, 0.2);
  color: #0d6efd;
  border: 1px solid rgba(13, 110, 253, 0.3);
}

.btn-info:hover {
  background: rgba(13, 110, 253, 0.3);
}

.btn-warning {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.btn-warning:hover {
  background: rgba(255, 193, 7, 0.3);
}

.btn-danger {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
  border: 1px solid rgba(220, 53, 69, 0.3);
}

.btn-danger:hover {
  background: rgba(220, 53, 69, 0.3);
}
</style>
