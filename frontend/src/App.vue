<template>
  <div class="app">
    <div v-if="currentView === 'home'" class="home-view">
      <header class="app-header">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
          </div>
          <div class="logo-text">
            <h1>Project Helper</h1>
            <p>项目学习助手</p>
          </div>
        </div>
      </header>

      <main class="main-content">
        <div class="input-section">
          <div class="input-container">
            <input v-model="repoUrl" type="text" placeholder="输入 GitHub 仓库地址..." @keyup.enter="addProject" />
            <button class="btn-add" @click="addProject" :disabled="loading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14" />
                <path d="M5 12h14" />
              </svg>
              分析项目
            </button>
          </div>
          <p class="hint">支持 GitHub HTTPS 和 SSH 地址格式</p>
        </div>

        <div class="projects-section">
          <h2 class="section-title">
            <span>已分析项目</span>
            <button class="btn-refresh" @click="loadProjects">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
                <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
                <path d="M16 21h5v-5" />
              </svg>
            </button>
          </h2>

          <div v-if="projects.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <p>还没有分析过任何项目</p>
            <p class="empty-hint">输入一个 GitHub 仓库地址开始分析</p>
          </div>

          <div v-else class="projects-grid">
            <ProjectCard v-for="project in projects" :key="project.id" :project="project"
              :progress-message="getProgressMessage(project.id)" @analyze="startAnalysis" @cancel="cancelAnalysis"
              @view-report="viewReport" @qa="openQA" @delete="deleteProject" @retry="retryAnalysis" />
          </div>
        </div>
      </main>
    </div>

    <ReportView v-else-if="currentView === 'report'" :project-id="selectedProjectId" :project-name="selectedProjectName"
      @back="goHome" />

    <QAInterface v-else-if="currentView === 'qa'" :project-id="selectedProjectId" @back="goHome" />
  </div>
</template>

<script setup>import { ref, onMounted, onUnmounted } from 'vue';
import ProjectCard from './components/ProjectCard.vue';
import ReportView from './components/ReportView.vue';
import QAInterface from './components/QAInterface.vue';
const repoUrl = ref('');
const projects = ref([]);
const currentView = ref('home');
const selectedProjectId = ref(null);
const selectedProjectName = ref('');
const loading = ref(false);
const progressMessages = ref({});
let pollingInterval = null;
const loadProjects = async () => {
  try {
    const response = await fetch('/api/projects');
    projects.value = await response.json();
  }
  catch (error) {
    console.error('Failed to load projects:', error);
  }
};
const addProject = async () => {
  if (!repoUrl.value.trim() || loading.value)
    return;
  loading.value = true;
  try {
    const response = await fetch('/api/projects', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ repo_url: repoUrl.value.trim() })
    });
    const project = await response.json();
    repoUrl.value = '';
    await loadProjects();
    startAnalysis(project.id);
  }
  catch (error) {
    console.error('Failed to add project:', error);
    alert('添加项目失败，请检查仓库地址是否正确');
  }
  finally {
    loading.value = false;
  }
};
const startAnalysis = async (projectId) => {
  try {
    const response = await fetch(`/api/analysis/${projectId}`, {
      method: 'POST'
    });
    await response.json();
    subscribeToProgress(projectId);
    await loadProjects();
  }
  catch (error) {
    console.error('Failed to start analysis:', error);
  }
};
const subscribeToProgress = (projectId) => {
  const eventSource = new EventSource(`/api/analysis/${projectId}/progress/stream`);
  eventSource.onmessage = (event) => {
    const data = event.data;
    if (data === 'completed' || data === 'failed' || data === 'cancelled') {
      eventSource.close();
      loadProjects();
    }
    else {
      progressMessages.value[projectId] = data;
    }
  };
  eventSource.onerror = () => {
    eventSource.close();
  };
};
const getProgressMessage = (projectId) => {
  return progressMessages.value[projectId] || '';
};
const viewReport = (projectId) => {
  const project = projects.value.find(p => p.id === projectId);
  if (project) {
    selectedProjectId.value = projectId;
    selectedProjectName.value = project.name;
    currentView.value = 'report';
  }
};
const openQA = (projectId) => {
  const project = projects.value.find(p => p.id === projectId);
  if (project) {
    selectedProjectId.value = projectId;
    selectedProjectName.value = project.name;
    currentView.value = 'qa';
  }
};
const cancelAnalysis = async (projectId) => {
  if (!confirm('确定要取消分析吗？'))
    return;
  try {
    await fetch(`/api/analysis/${projectId}/cancel`, {
      method: 'POST'
    });
    await loadProjects();
  }
  catch (error) {
    console.error('Failed to cancel analysis:', error);
  }
};
const deleteProject = async (projectId) => {
  if (!confirm('确定要删除这个项目吗？'))
    return;
  try {
    await fetch(`/api/projects/${projectId}`, {
      method: 'DELETE'
    });
    await loadProjects();
  }
  catch (error) {
    console.error('Failed to delete project:', error);
  }
};
const retryAnalysis = (projectId) => {
  startAnalysis(projectId);
};
const goHome = () => {
  currentView.value = 'home';
  selectedProjectId.value = null;
  selectedProjectName.value = '';
  loadProjects();
};
const startPolling = () => {
  if (pollingInterval) clearInterval(pollingInterval);
  pollingInterval = setInterval(() => {
    loadProjects();
  }, 3000);
};

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
};

onMounted(() => {
  loadProjects();
  startPolling();
});

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
.app {
  min-height: 100vh;
}

.home-view {
  min-height: 100vh;
}

.app-header {
  padding: 24px 40px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-icon svg {
  width: 28px;
  height: 28px;
}

.logo-text h1 {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.logo-text p {
  font-size: 13px;
  color: #a0aec0;
  margin: 4px 0 0;
}

.main-content {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.input-section {
  text-align: center;
  margin-bottom: 48px;
}

.input-container {
  display: flex;
  max-width: 700px;
  margin: 0 auto;
  gap: 12px;
}

.input-container input {
  flex: 1;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: white;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease;
}

.input-container input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
}

.input-container input::placeholder {
  color: #718096;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 16px;
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-add:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.btn-add:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-add svg {
  width: 20px;
  height: 20px;
}

.hint {
  margin-top: 12px;
  color: #718096;
  font-size: 14px;
}

.projects-section {
  margin-top: 40px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.btn-refresh {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #a0aec0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-refresh:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-refresh svg {
  width: 18px;
  height: 18px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px dashed rgba(255, 255, 255, 0.1);
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: #667eea;
}

.empty-icon svg {
  width: 40px;
  height: 40px;
}

.empty-state p {
  color: #a0aec0;
  margin: 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: #718096 !important;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}
</style>
