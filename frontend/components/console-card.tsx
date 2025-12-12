"use client"

import { useEffect, useRef } from "react"
import { Terminal } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { LogEntry } from "@/hooks/use-quantum-socket"

interface ConsoleCardProps {
  logs: LogEntry[]
}

export function ConsoleCard({ logs }: ConsoleCardProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  const getLogColor = (type: LogEntry["type"]) => {
    switch (type) {
      case "success":
        return "text-[#39FF14]"
      case "error":
        return "text-destructive"
      case "reasoning":
        return "text-blue-400"
      default:
        return "text-muted-foreground"
    }
  }

  return (
    <Card className="border-border bg-card">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Terminal className="h-4 w-4 text-[#39FF14]" />
          Quantum Console
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          ref={scrollRef}
          className="terminal-scroll h-[280px] overflow-y-auto rounded-lg border border-border bg-background/50 p-3 font-mono text-xs"
        >
          {logs.length === 0 ? (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              <span className="animate-pulse">Awaiting connection...</span>
            </div>
          ) : (
            logs.map((log) => (
              <div key={log.id} className="mb-1 leading-relaxed">
                <span className="text-muted-foreground/60">[{new Date(log.timestamp).toLocaleTimeString()}]</span>{" "}
                <span className={getLogColor(log.type)}>{log.message}</span>
              </div>
            ))
          )}
          <div className="mt-2 flex items-center gap-1">
            <span className="text-[#39FF14]">❯</span>
            <span className="animate-pulse text-[#39FF14]">_</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
