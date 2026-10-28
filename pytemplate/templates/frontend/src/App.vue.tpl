<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { httpGet } from './api/http'
import { WsChannel } from './api/ws'

const projectName = '{{PROJECT_NAME}}'
const healthText = ref<string>('检测中 ...')
const wsText = ref<string>('未连接')

interface HealthPayload {
  status: string
  app: string
  mode: string
}

async function refreshHealth(): Promise<void> {
  try {
    const data = await httpGet<HealthPayload>('/health')
    healthText.value = `status=${data.status}, mode=${data.mode}`
  } catch (error) {
    healthText.value = `请求失败: ${String(error)}`
  }
}

onMounted(() => {
  void refreshHealth()
  const channel = new WsChannel(import.meta.env.VITE_WS_URL)
  channel.onOpen(() => {
    wsText.value = '已连接'
  })
  channel.onMessage((data) => {
    wsText.value = `收到 ${data.byteLength} 字节`
  })
})
</script>

<template>
  <main class="home">
    <h1>{{ projectName }}</h1>
    <p>HTTP 健康检查: {{ healthText }}</p>
    <p>WebSocket RPC: {{ wsText }}</p>
  </main>
</template>

<style scoped>
.home {
  max-width: 720px;
  margin: 60px auto;
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
  color: #303133;
}
.home p {
  color: #606266;
}
</style>
