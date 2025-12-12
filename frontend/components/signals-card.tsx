"use client"

import { Activity, ArrowUpRight, ArrowDownRight } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Signal } from "@/hooks/use-quantum-socket"

interface SignalsCardProps {
  signals: Signal[]
}

export function SignalsCard({ signals }: SignalsCardProps) {
  return (
    <Card className="border-border bg-card">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-sm font-medium text-muted-foreground">
          <span className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-[#39FF14]" />
            Live Signals
          </span>
          <Badge variant="secondary" className="bg-secondary text-muted-foreground">
            {signals.length} Active
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {signals.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">No active signals</div>
          ) : (
            signals.map((signal) => (
              <div
                key={signal.id}
                className="flex items-center justify-between rounded-lg border border-border bg-secondary/30 p-3 transition-colors hover:bg-secondary/50"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                      signal.type === "BUY" ? "bg-[#39FF14]/10 text-[#39FF14]" : "bg-destructive/10 text-destructive"
                    }`}
                  >
                    {signal.type === "BUY" ? (
                      <ArrowUpRight className="h-4 w-4" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4" />
                    )}
                  </div>
                  <div>
                    <p className="font-mono text-sm font-medium text-foreground">{signal.symbol}</p>
                    <p className="text-xs text-muted-foreground">
                      {signal.type} @ {signal.openPrice.toFixed(signal.openPrice < 100 ? 4 : 2)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p
                    className={`font-mono text-sm font-semibold ${
                      signal.profit >= 0 ? "text-[#39FF14]" : "text-destructive"
                    }`}
                  >
                    {signal.profit >= 0 ? "+" : ""}${signal.profit.toFixed(2)}
                  </p>
                  <p className="text-xs text-muted-foreground">{new Date(signal.timestamp).toLocaleTimeString()}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
