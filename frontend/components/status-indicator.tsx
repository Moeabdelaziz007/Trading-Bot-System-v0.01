"use client"

import { Download, Wifi, WifiOff, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface StatusIndicatorProps {
  isConnected: boolean
  isConnecting: boolean
  onConnect: () => void
  onDownload: () => void
}

export function StatusIndicator({ isConnected, isConnecting, onConnect, onDownload }: StatusIndicatorProps) {
  return (
    <div className="flex items-center gap-3">
      {!isConnected && !isConnecting && (
        <Button
          variant="outline"
          size="sm"
          onClick={onDownload}
          className="border-border bg-secondary/50 text-muted-foreground hover:bg-secondary hover:text-foreground"
        >
          <Download className="mr-2 h-4 w-4" />
          Download Engine
        </Button>
      )}

      <button
        onClick={onConnect}
        disabled={isConnecting || isConnected}
        className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 transition-all hover:bg-secondary/50 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isConnecting ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin text-[#39FF14]" />
            <span className="text-sm text-muted-foreground">Connecting...</span>
          </>
        ) : isConnected ? (
          <>
            <Wifi className="h-4 w-4 text-[#39FF14]" />
            <span className="text-sm font-medium text-[#39FF14]">Connected</span>
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#39FF14] opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-[#39FF14]"></span>
            </span>
          </>
        ) : (
          <>
            <WifiOff className="h-4 w-4 text-destructive" />
            <span className="text-sm text-muted-foreground">Disconnected</span>
            <span className="h-2 w-2 rounded-full bg-destructive"></span>
          </>
        )}
      </button>
    </div>
  )
}
