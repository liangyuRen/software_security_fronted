<template>
  <div class="chat-frame" >

    <div class="chat-header">
      <h1>安全小助手</h1>
      <button class="close-button" @click="$emit('closeBody')">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="close-icon">
          <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>

    <div class="chat-messages">

      <div v-for="message in messages" :key="message.timestamp" class="message-container">
        <!-- assistant message -->
        <div class="message assistant-message" v-if="message.isAssistant">
          <div class="avatar assistant-avatar">
            <el-icon style="color: white"><Orange></Orange></el-icon>
          </div>
          <div class="message-content">
            {{ message.content }}
          </div>
        </div>

        <!-- user message -->
        <div class="message user-message" v-else>
          <div class="avatar user-avatar">
            <span>U</span>
          </div>
          <div class="message-content">
            {{ message.content }}
          </div>
        </div>
      </div>
    </div>

    <!-- input -->
    <div class="input-container">
      <div class="model-selector">
        <div class="model-selector-button" @click="showModelSelector = !showModelSelector" >
          <span>{{selectedModel == '' ? '选择模型':selectedModel}}</span>
          <div class="model-selector-icon" :class="showModelSelector ? 'open' : ''">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="assistant-icon">
              <path d="M12 15l-6-6h12z" fill="currentColor"/>
            </svg>
          </div>

        </div>
        <div class="model-selector-options" v-show="showModelSelector">
          <div v-for="option in modelOptions" :key="option.value" class="model-selector-option" @click="selectedModel = option.value; showModelSelector = false">
            {{ option.label }}
          </div>
        </div>
      </div>
      <div class="input-area">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="请输入希望问小助手的问题..."
          @keyup.enter="sendMessage"
        >
        <button class="send-button" @click="sendMessage">发送</button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {Orange} from "@element-plus/icons-vue";
import {queryLLM} from "@/components/LLMHelper/apis.ts";

interface Message {
  content: string
  isAssistant: boolean
  timestamp: number
}

const inputMessage = ref('')
const messages = ref<Message[]>([
  {
    content: '您好！我是您的项目安全漏洞管理助手，随时为您提供安全漏洞的检测、修复建议和管理指导。请问有什么可以帮您？',
    isAssistant: true,
    timestamp: Date.now()
  },
  {
    content: '您好！很高兴遇见您！',
    isAssistant: false,
    timestamp: Date.now()
  }
])
const modelOptions = [
  {
    value: 'qwen',
    label: 'qwen'
  },
  {
    value: 'DeepSeek',
    label: 'DeepSeek'
  },
  {
    value: 'Llama',
    label: 'Llama'
  }
]
const selectedModel = ref('')
const showModelSelector = ref(false)

const sendMessage = () => {
  if (!inputMessage.value.trim()) return

  const newMessage: Message = {
    content: inputMessage.value,
    isAssistant: false,
    timestamp: Date.now()
  }

  messages.value.push(newMessage)

  // simulate assistant response
  // setTimeout(() => {
  //   const assistantResponse: Message = {
  //     content: '我很乐意帮助您解决问题，请详细描述您遇到的情况。',
  //     isAssistant: true,
  //     timestamp: Date.now()
  //   }
  //   messages.value.push(assistantResponse)
  // }, 1000)

  // query assistant response
  queryLLM(inputMessage.value, selectedModel.value == '选择模型' ? '':selectedModel.value).then((res) => {
    function pushError() {
      const assistantResponse: Message = {
        content: '服务器繁忙，请稍后再试。',
        isAssistant: true,
        timestamp: Date.now()
      }
      messages.value.push(assistantResponse)
    }

    console.log(res)
    if(res.data.code !== 200) {
      pushError()
      return
    }
    const assistantResponse: Message = {
      content: res.data.obj,
      isAssistant: true,
      timestamp: Date.now()
    }
    messages.value.push(assistantResponse)
  }).catch((err) => {
    console.log(err)
    pushError()
  })

  // clear input
  inputMessage.value = ''

  //store only the last 10 messages
  if (messages.value.length > 10) {
    messages.value.shift()
  }
}

</script>

<style scoped>
.chat-frame {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  min-height: 500px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.chat-header h1 {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.close-icon {
  width: 20px;
  height: 20px;
  color: #57606a;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 500px;
}

.message-container {
  display: flex;
  flex-direction: column;
  gap: 8px;

}

.message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  max-width: 80%;
}

.user-message {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.avatar {
  min-width: 32px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.assistant-avatar {
  background-color: #4169E1;
}

.user-avatar {
  background-color: #e5e5e5;

  span{
    color: #24292f;
    font-size: 18px;
    font-weight: 700;
  }
}

.assistant-icon {
  width: 20px;
  height: 20px;
  fill: white;
}

.message-content {
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
}

.assistant-message .message-content {
  background-color: #4169E1;
  color: white;
}

.user-message .message-content {
  background-color: #f5f5f5;
  color: #333;
}

.model-selector {
  position: relative;
  margin-left: 16px;
  width: 125px;
}

.model-selector-button{
  padding: 4px 12px;
  border: 1px solid #ddd;
  border-radius: 16px;
  cursor: pointer;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;

  span{
    font-weight: bold;
    color: #1e1e1e;
  }

  .model-selector-icon{
    width: 20px;
    height: 20px;
    fill: #1e1e1e;
    transition: transform 0.4s;
  }

  .model-selector-icon.open {
    transform: rotate(180deg);
  }
}

.model-selector-button:hover {
  background-color: #f5f5f5;
  color: #3a3a3a;
  transition: all 0.4s;
}

.model-selector-options {
  width: 100%;
  position: absolute;
  bottom: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1;
  animation: slide-down 0.4s;
}

@keyframes slide-down {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.model-selector-option {
  padding: 4px 12px;
  cursor: pointer;
  border-radius: 8px;
  font-size: 14px;
  color: grey;
  transition: background-color 0.4s;
}

.model-selector-option:hover {
  background-color: #f5f5f5;
}

.input-container{
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  gap: 8px;
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 0 16px;
}

.input-area input {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 16px;
  font-size: 14px;
  outline: none;
}

.input-area input:focus {
  border-color: #4169E1;
}

.send-button {
  background-color: #4169E1;
  color: white;
  border: none;
  border-radius: 16px;
  padding: 4px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: background-color 0.2s;
}

.send-button:hover {
  background-color: #3154b3;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-track {
  background-color: rgba(0, 0, 0, 0.05);
}

@media (max-width: 480px) {
  .chat-frame {
    height: 100vh;
    max-width: 100%;
    border-radius: 0;
  }

  .message {
    max-width: 90%;
  }
}
</style>
