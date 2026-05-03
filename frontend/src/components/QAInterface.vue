<template>
  <div class="qa-interface">
    <div class="qa-header">
      <button class="btn-back" @click="$emit('back')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5"/>
          <path d="M12 19l-7-7 7-7"/>
        </svg>
        返回
      </button>
      <h2 class="qa-title">交互式问答</h2>
    </div>
    
    <div class="qa-history">
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        class="message"
        :class="{ 'user': msg.type === 'user', 'assistant': msg.type === 'assistant' }"
      >
        <div class="avatar">
          {{ msg.type === 'user' ? 'U' : 'A' }}
        </div>
        <div class="message-content">
          <p>{{ msg.content }}</p>
        </div>
      </div>
      
      <div v-if="loading" class="loading-message">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
    
    <div class="qa-input">
      <input 
        v-model="question"
        type="text" 
        placeholder="输入你想询问的问题..."
        @keyup.enter="sendQuestion"
        :disabled="loading"
      />
      <button class="btn-send" @click="sendQuestion" :disabled="loading || !question.trim()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 2L11 13"/>
          <path d="M22 2L15 22L11 13L2 9"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>import { ref } from 'vue';
const props = defineProps({
 projectId: {
 type: Number,
 required: true
 }
});
defineEmits(['back']);
const question = ref('');
const messages = ref([]);
const loading = ref(false);
const sendQuestion = async () => {
 if (!question.value.trim() || loading.value)
 return;
 const userQuestion = question.value.trim();
 messages.value.push({
 type: 'user',
 content: userQuestion
 });
 question.value = '';
 loading.value = true;
 try {
 const response = await fetch('/api/qa', {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json'
 },
 body: JSON.stringify({
 project_id: props.projectId,
 question: userQuestion
 })
 });
 const data = await response.json();
 messages.value.push({
 type: 'assistant',
 content: data.answer
 });
 }
 catch (error) {
 messages.value.push({
 type: 'assistant',
 content: '抱歉，回答问题时出错了。'
 });
 }
 finally {
 loading.value = false;
 }
};
</script>

<style scoped>
.qa-interface {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 40px);
  padding: 20px;
}

.qa-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
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

.qa-title {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.qa-history {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
}

.message.assistant {
  align-self: flex-start;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.message.user .avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message.assistant .avatar {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
}

.message-content {
  background: rgba(255, 255, 255, 0.05);
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.message.user .message-content {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
}

.message-content p {
  margin: 0;
  color: #e2e8f0;
  line-height: 1.6;
  font-size: 14px;
}

.loading-message {
  display: flex;
  justify-content: flex-start;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

.qa-input {
  display: flex;
  gap: 12px;
}

.qa-input input {
  flex: 1;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}

.qa-input input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.qa-input input::placeholder {
  color: #718096;
}

.qa-input input:disabled {
  opacity: 0.5;
}

.btn-send {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-send svg {
  width: 20px;
  height: 20px;
}
</style>
