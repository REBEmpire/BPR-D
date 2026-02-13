"use client"

import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { ExternalLink, Zap } from "lucide-react"
import { useGamification } from "@/context/gamification-context"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"

export default function AiCommHubPage() {
  const { completeQuest, isRussell } = useGamification()
  const [triggerStatus, setTriggerStatus] = useState<"idle" | "loading" | "success">("idle")

  const handleTestTrigger = async () => {
    setTriggerStatus("loading")
    // Mock API call
    setTimeout(() => {
      setTriggerStatus("success")
      if (isRussell) {
        completeQuest("q3", 30) // Quest: Test n8n Integration
      }
      setTimeout(() => setTriggerStatus("idle"), 2000)
    }, 1500)
  }

  return (
    <div className="container mx-auto p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">AI Communications Hub</h1>
          <p className="text-muted-foreground text-lg">
            Central automation relay powered by n8n.
          </p>
        </div>
        <Badge className="bg-green-500 hover:bg-green-600">Live System</Badge>
      </div>

      <div className="grid gap-8 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Control Center</CardTitle>
            <CardDescription>Direct access to automation workflows.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              className="w-full h-12 text-lg"
              asChild
              disabled={!process.env.NEXT_PUBLIC_N8N_WORKFLOW_URL}
            >
              <a
                href={process.env.NEXT_PUBLIC_N8N_WORKFLOW_URL || "#"}
                target="_blank"
                rel="noopener noreferrer"
                className={!process.env.NEXT_PUBLIC_N8N_WORKFLOW_URL ? "pointer-events-none opacity-50" : ""}
              >
                <ExternalLink className="mr-2 h-5 w-5" />
                Open n8n Instance
              </a>
            </Button>

            <div className="pt-4 border-t">
              <h3 className="font-semibold mb-2">Testing</h3>
              <div className="flex items-center gap-4">
                <Button
                  variant="secondary"
                  onClick={handleTestTrigger}
                  disabled={triggerStatus === "loading"}
                >
                  <Zap className="mr-2 h-4 w-4" />
                  {triggerStatus === "loading" ? "Firing..." : "Test Trigger"}
                </Button>
                {triggerStatus === "success" && (
                  <span className="text-green-600 font-medium text-sm animate-in fade-in">
                    Webhook fired successfully!
                  </span>
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Sends a test payload to the Telegram relay workflow.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Uptime</span>
                <span className="font-mono">99.9%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Active Workflows</span>
                <span className="font-mono">12</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Last Execution</span>
                <span className="font-mono">2m ago</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
