"use client"

import { useState, useEffect, useCallback, useRef } from "react"

export interface AccountData {
  balance: number
  equity: number
  profit: number
}

export interface Signal {
  id: string
  symbol: string
  type: "BUY" | "SELL"
  profit: number
  openPrice: number
  currentPrice: number
  timestamp: Date
}

export interface LogEntry {
  id: string
  timestamp: Date
  message: string
  type: "info" | "success" | "error" | "reasoning"
}

export interface QuantumState {
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  account: AccountData
  signals: Signal[]
  logs: LogEntry[]
}

const MOCK_ACCOUNT: AccountData = {
  balance: 125847.32,
  equity: 128492.18,
  profit: 2644.86,
}

const MOCK_SIGNALS: Signal[] = [
  {
    id: "sig-001",
    symbol: "EUR/USD",
    type: "BUY",
    profit: 847.23,
    openPrice: 1.0842,
    currentPrice: 1.0891,
    timestamp: new Date(Date.now() - 3600000),
  },
  {
    id: "sig-002",
    symbol: "BTC/USD",
    type: "SELL",
    profit: -124.5,
    openPrice: 43250.0,
    currentPrice: 43374.5,
    timestamp: new Date(Date.now() - 7200000),
  },
  {
    id: "sig-003",
    symbol: "GOLD",
    type: "BUY",
    profit: 1921.13,
    openPrice: 2024.5,
    currentPrice: 2043.75,
    timestamp: new Date(Date.now() - 1800000),
  },
]

const MOCK_LOGS: LogEntry[] = [
  {
    id: "log-001",
    timestamp: new Date(Date.now() - 60000),
    message: "[QUANTUM] Initializing neural pattern recognition...",
    type: "info",
  },
  {
    id: "log-002",
    timestamp: new Date(Date.now() - 55000),
    message: "[REASONING] Analyzing EUR/USD: RSI divergence detected at 1.0842",
    type: "reasoning",
  },
  {
    id: "log-003",
    timestamp: new Date(Date.now() - 50000),
    message: "[SIGNAL] BUY EUR/USD executed @ 1.0842 | Confidence: 87.3%",
    type: "success",
  },
  {
    id: "log-004",
    timestamp: new Date(Date.now() - 45000),
    message: "[REASONING] BTC showing bearish momentum, MACD crossover imminent",
    type: "reasoning",
  },
  {
    id: "log-005",
    timestamp: new Date(Date.now() - 40000),
    message: "[SIGNAL] SELL BTC/USD executed @ 43250 | Confidence: 72.1%",
    type: "success",
  },
]

export function useQuantumSocket() {
  const [state, setState] = useState<QuantumState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    account: MOCK_ACCOUNT,
    signals: MOCK_SIGNALS,
    logs: MOCK_LOGS,
  })

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const addLog = useCallback((message: string, type: LogEntry["type"] = "info") => {
    const newLog: LogEntry = {
      id: `log-${Date.now()}`,
      timestamp: new Date(),
      message,
      type,
    }
    setState((prev) => ({
      ...prev,
      logs: [...prev.logs.slice(-49), newLog],
    }))
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    setState((prev) => ({ ...prev, isConnecting: true, error: null }))
    addLog("[SYSTEM] Attempting connection to Quantum Engine...", "info")

    try {
      const ws = new WebSocket("wss://localhost:8765")

      ws.onopen = () => {
        setState((prev) => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          error: null,
        }))
        addLog("[SYSTEM] Connected to Quantum Engine ✓", "success")
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === "account") {
            setState((prev) => ({ ...prev, account: data.payload }))
          } else if (data.type === "signal") {
            setState((prev) => ({
              ...prev,
              signals: [...prev.signals, data.payload],
            }))
            addLog(`[SIGNAL] ${data.payload.type} ${data.payload.symbol}`, "success")
          } else if (data.type === "log") {
            addLog(data.payload.message, data.payload.logType || "info")
          }
        } catch {
          addLog(`[DATA] ${event.data}`, "info")
        }
      }

      ws.onerror = () => {
        setState((prev) => ({
          ...prev,
          isConnecting: false,
          error: "Connection failed. Is the engine running?",
        }))
        addLog("[ERROR] WebSocket connection error", "error")
      }

      ws.onclose = () => {
        setState((prev) => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
        }))
        addLog("[SYSTEM] Disconnected from Quantum Engine", "error")
        wsRef.current = null
      }

      wsRef.current = ws
    } catch {
      setState((prev) => ({
        ...prev,
        isConnecting: false,
        error: "Failed to create WebSocket connection",
      }))
      addLog("[ERROR] Failed to initialize WebSocket", "error")
    }
  }, [addLog])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [])

  const sendCommand = useCallback((command: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(command))
      return true
    }
    return false
  }, [])

  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    ...state,
    connect,
    disconnect,
    sendCommand,
    addLog,
  }
}
