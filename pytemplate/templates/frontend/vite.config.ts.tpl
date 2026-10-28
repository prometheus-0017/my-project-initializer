import { defineConfig, type PluginOption } from 'vite'
import vue from '@vitejs/plugin-vue'

/** external 构建时的外部模块 → CDN 地址(import map 注入用)。 */
const CDN_IMPORTS: Record<string, string> = {
  vue: 'https://cdn.jsdelivr.net/npm/vue@3.4.31/dist/vue.esm-browser.prod.js',{{EXTERNAL_CDN_ENTRY}}
}

/** external 构建时向 index.html 注入 import map,使产物直接引用外部库。 */
function injectImportMap(): PluginOption {
  return {
    name: 'inject-external-import-map',
    apply: 'build',
    transformIndexHtml() {
      return [
        {
          tag: 'script',
          attrs: { type: 'importmap' },
          children: JSON.stringify({ imports: CDN_IMPORTS }),
          injectTo: 'head',
        },
      ]
    },
  }
}

export default defineConfig(({ mode }) => {
  const isExternal = mode === 'external'
  return {
    plugins: [vue(), ...(isExternal ? [injectImportMap()] : [])],
    server: {
      port: {{FRONTEND_DEV_PORT}},
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:{{BACKEND_DEV_HTTP_PORT}}',
          changeOrigin: true,
        },
      },
    },
    build: isExternal
      ? { rollupOptions: { external: [{{EXTERNAL_PACKAGES}}] } }
      : undefined,
  }
})
