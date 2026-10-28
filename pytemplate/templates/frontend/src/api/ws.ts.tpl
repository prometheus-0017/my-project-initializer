/**
 * WebSocket 通道封装(二进制帧)。
 *
 * 后端使用 xuri-rpc-websocket(CBOR 二进制协议);业务侧可配合 cbor-x 等
 * JS 库对本通道的帧内容进行编解码,进而实现 xuri-rpc 的对象/回调调用。
 * 连接断开后自动按指数退避重连,直到调用 close() 主动关闭。
 */
export class WsChannel {
  private ws: WebSocket | null = null
  private retryDelayMs = 1000
  private closedByUser = false
  private readonly messageHandlers = new Set<(data: ArrayBuffer) => void>()
  private readonly openHandlers = new Set<() => void>()

  constructor(private readonly url: string) {
    this.connect()
  }

  /** 注册消息回调(二进制帧)。 */
  onMessage(handler: (data: ArrayBuffer) => void): this {
    this.messageHandlers.add(handler)
    return this
  }

  /** 注册连接建立回调。 */
  onOpen(handler: () => void): this {
    this.openHandlers.add(handler)
    return this
  }

  /** 发送二进制帧;未连接时显式抛错。 */
  send(payload: ArrayBuffer): void {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket 未连接,发送失败')
    }
    this.ws.send(payload)
  }

  /** 主动关闭并停止自动重连。 */
  close(): void {
    this.closedByUser = true
    this.ws?.close()
  }

  private connect(): void {
    this.ws = new WebSocket(this.url)
    this.ws.binaryType = 'arraybuffer'
    this.ws.onopen = () => {
      this.retryDelayMs = 1000
      this.openHandlers.forEach((handler) => handler())
    }
    this.ws.onmessage = (event: MessageEvent) => {
      if (event.data instanceof ArrayBuffer) {
        this.messageHandlers.forEach((handler) => handler(event.data as ArrayBuffer))
      }
    }
    this.ws.onclose = () => {
      if (!this.closedByUser) {
        this.reconnectLater()
      }
    }
  }

  private reconnectLater(): void {
    window.setTimeout(() => this.connect(), this.retryDelayMs)
    this.retryDelayMs = Math.min(this.retryDelayMs * 2, 30000)
  }
}
