<template>
  <div class="report-view">
    <div class="report-header">
      <button class="btn-back" @click="$emit('back')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5"/>
          <path d="M12 19l-7-7 7-7"/>
        </svg>
        返回
      </button>
      <h2 class="report-title">{{ projectName }}</h2>
    </div>
    
    <div class="report-content" v-if="report">
      <div v-html="renderedMarkdown"></div>
    </div>
    
    <div v-else class="loading-report">
      <div class="spinner"></div>
      <p>加载报告中...</p>
    </div>
  </div>
</template>

<script setup>import { ref, watch, onMounted } from 'vue';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';
const props = defineProps({
 projectId: {
 type: Number,
 required: true
 },
 projectName: {
 type: String,
 default: ''
 }
});
defineEmits(['back']);
const report = ref('');
marked.setOptions({
 highlight: function (code, lang) {
 if (lang && hljs.getLanguage(lang)) {
 try {
 return hljs.highlight(code, { language: lang }).value;
 }
 catch (__) { }
 }
 return hljs.highlightAuto(code).value;
 }
});
const renderedMarkdown = ref('');
const loadReport = async () => {
 try {
 const response = await fetch(`/api/analysis/${props.projectId}/report`);
 const data = await response.json();
 report.value = data.report;
 renderedMarkdown.value = marked(data.report);
 }
 catch (error) {
 console.error('Failed to load report:', error);
 }
};
onMounted(() => {
 loadReport();
});
watch(() => props.projectId, () => {
 loadReport();
});
</script>

<style scoped>
.report-view {
  min-height: 100vh;
  padding: 20px;
}

.report-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-back svg {
  width: 18px;
  height: 18px;
}

.report-title {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.report-content {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.report-content :deep(h1) {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 24px 0 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.report-content :deep(h2) {
  font-size: 22px;
  font-weight: 600;
  color: #fff;
  margin: 20px 0 12px;
}

.report-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 16px 0 10px;
}

.report-content :deep(p) {
  color: #a0aec0;
  line-height: 1.8;
  margin: 12px 0;
}

.report-content :deep(ul), .report-content :deep(ol) {
  color: #a0aec0;
  padding-left: 24px;
  margin: 12px 0;
}

.report-content :deep(li) {
  margin: 8px 0;
  line-height: 1.6;
}

.report-content :deep(code) {
  background: rgba(102, 126, 234, 0.2);
  color: #e2e8f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
}

.report-content :deep(pre) {
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  padding: 20px;
  overflow-x: auto;
  margin: 16px 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.report-content :deep(pre code) {
  background: transparent;
  padding: 0;
  font-size: 14px;
}

.report-content :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding: 12px 20px;
  background: rgba(102, 126, 234, 0.1);
  margin: 16px 0;
  color: #a0aec0;
}

.loading-report {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(102, 126, 234, 0.3);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-report p {
  margin-top: 20px;
  color: #a0aec0;
}
</style>
