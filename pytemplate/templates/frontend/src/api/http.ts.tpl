/**
 * 极简 HTTP 客户端:统一 /api 前缀,非 2xx 直接抛错(不静默)。
 * 开发期经 vite 代理转发到后端 dev 端口;生产环境与 flask 同源。
 */
export async function httpGet<T>(path: string): Promise<T> {
  const resp = await fetch(`/api${path}`)
  if (!resp.ok) {
    throw new Error(`GET /api${path} 失败: HTTP ${resp.status}`)
  }
  return (await resp.json()) as T
}

export async function httpPost<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(`/api${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!resp.ok) {
    throw new Error(`POST /api${path} 失败: HTTP ${resp.status}`)
  }
  return (await resp.json()) as T
}
