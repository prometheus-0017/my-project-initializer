/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 后端 WebSocket RPC 地址(按环境由 .env.* 注入)。 */
  readonly VITE_WS_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
