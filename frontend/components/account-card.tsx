"use client"

import { TrendingUp, TrendingDown, Wallet, BarChart3, DollarSign } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { AccountData } from "@/hooks/use-quantum-socket"

interface AccountCardProps {
  account: AccountData
}

export function AccountCard({ account }: AccountCardProps) {
  const isProfit = account.profit >= 0

  return (
    <Card className="border-border bg-card">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Wallet className="h-4 w-4 text-[#39FF14]" />
          Account Overview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <DollarSign className="h-3 w-3" />
            Balance
          </div>
          <p className="font-mono text-3xl font-bold tracking-tight text-foreground">
            ${account.balance.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <BarChart3 className="h-3 w-3" />
              Equity
            </div>
            <p className="font-mono text-xl font-semibold text-foreground">
              ${account.equity.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            </p>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              {isProfit ? (
                <TrendingUp className="h-3 w-3 text-[#39FF14]" />
              ) : (
                <TrendingDown className="h-3 w-3 text-destructive" />
              )}
              Profit/Loss
            </div>
            <p className={`font-mono text-xl font-semibold ${isProfit ? "text-[#39FF14]" : "text-destructive"}`}>
              {isProfit ? "+" : ""}${account.profit.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            </p>
          </div>
        </div>

        <div className="h-1 w-full overflow-hidden rounded-full bg-secondary">
          <div
            className="h-full rounded-full bg-[#39FF14] transition-all duration-500"
            style={{
              width: `${Math.min((account.equity / account.balance) * 100, 100)}%`,
            }}
          />
        </div>
      </CardContent>
    </Card>
  )
}
