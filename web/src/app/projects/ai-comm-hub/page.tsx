"use client"

import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import { ExternalLink, Zap, Users, FileText, CheckCircle2, XCircle, Loader2 } from "lucide-react"
import { useGamification } from "@/context/gamification-context"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"

type TriggerStatus = "idle" | "loading" | "success" | "error"

const AGENTS = [
  { id: "grok", label: "Grok", role: "Chief", available: true },
  { id: "claude", label: "Claude", role: "Strategist", available: true },
  { id: "gemini", label: "Gemini", role: "Lead Dev", available: true },
  { id: "abacus", label: "Abacus", role: "Innovator", available: false },
]

const MEETING_TYPES = [
  { value: "daily_briefing", label: "Team Briefing (recommended)" },
  { value: "work_session", label: "Work Session (solo agent)" },
]

export default function AiCommHubPage() {
  const { completeQuest, isRussell } = useGamification()

  // Legacy test trigger state
  const [triggerStatus, setTriggerStatus] = useState<"idle" | "loading" | "success">("idle")

  // HiC meeting dialog state
  const [dialogOpen, setDialogOpen] = useState(false)
  const [goal, setGoal] = useState("")
  const [brief, setBrief] = useState("")
  const [meetingType, setMeetingType] = useState("daily_briefing")
  const [selectedAgents, setSelectedAgents] = useState<string[]>(["grok", "claude", "gemini"])
  const [fireStatus, setFireStatus] = useState<TriggerStatus>("idle")
  const [fireResult, setFireResult] = useState<{
    meeting_id?: string
    report_url?: string
    cost_usd?: number
    error?: string
  } | null>(null)

  const toggleAgent = (id: string) => {
    setSelectedAgents((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    )
  }

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

  const handleFireMeeting = async () => {
    if (!goal.trim() && !brief.trim()) return
    if (selectedAgents.length === 0) return

    setFireStatus("loading")
    setFireResult(null)

    try {
      const res = await fetch("/api/hic/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          meeting_type: meetingType,
          participants: selectedAgents,
          goal: goal.trim(),
          custom_prompt: brief.trim() || undefined,
        }),
      })

      const data = await res.json()

      if (!res.ok) {
        setFireStatus("error")
        setFireResult({ error: data.error || data.detail || "Meeting service returned an error." })
      } else {
        setFireStatus("success")
        setFireResult({
          meeting_id: data.meeting_id,
          report_url: data.report_url,
          cost_usd: data.cost_usd,
        })
        if (isRussell) {
          completeQuest("q3", 50)
        }
      }
    } catch (err) {
      console.error("[HiC trigger] fetch failed:", err)
      setFireStatus("error")
      setFireResult({ error: "Could not reach the server. Check your connection." })
    }
  }

  const resetDialog = () => {
    setGoal("")
    setBrief("")
    setMeetingType("daily_briefing")
    setSelectedAgents(["grok", "claude", "gemini"])
    setFireStatus("idle")
    setFireResult(null)
  }

  return (
    <div className="container mx-auto p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">AI Communications Hub</h1>
          <p className="text-muted-foreground text-lg">
            Central automation relay — trigger team meetings, monitor workflows.
          </p>
        </div>
        <Badge className="bg-green-500 hover:bg-green-600">Live System</Badge>
      </div>

      <div className="grid gap-8 max-w-2xl">

        {/* HiC Team Meeting Trigger */}
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-500" />
              Fire Team Meeting
            </CardTitle>
            <CardDescription>
              Assemble any combination of agents around a goal or brief. They will
              collaborate with full dialogue and commit deliverables to GitHub.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              className="w-full h-12 text-base font-semibold"
              onClick={() => { resetDialog(); setDialogOpen(true) }}
            >
              <Users className="mr-2 h-5 w-5" />
              Assemble the Team
            </Button>
          </CardContent>
        </Card>

        {/* Dialog */}
        <Dialog open={dialogOpen} onOpenChange={(open) => { if (!open) resetDialog(); setDialogOpen(open) }}>
          <DialogContent className="max-w-xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-xl">
                <Zap className="h-5 w-5 text-yellow-500" />
                Fire Team Meeting
              </DialogTitle>
              <DialogDescription>
                Set the goal and brief. The team will read it as a HiC Directive — top priority.
              </DialogDescription>
            </DialogHeader>

            {fireStatus === "idle" || fireStatus === "loading" ? (
              <div className="space-y-5 py-2">

                {/* Goal */}
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">
                    Goal <span className="text-destructive">*</span>
                  </label>
                  <Input
                    placeholder="e.g. Implement hybrid semantic search in discovery.py"
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    disabled={fireStatus === "loading"}
                  />
                  <p className="text-xs text-muted-foreground">One sentence — what do you want done?</p>
                </div>

                {/* Full Brief */}
                <div className="space-y-1.5">
                  <label className="text-sm font-medium flex items-center gap-1">
                    <FileText className="h-3.5 w-3.5" />
                    Full Brief
                    <span className="text-muted-foreground font-normal ml-1">(optional)</span>
                  </label>
                  <textarea
                    className="w-full min-h-[140px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-y font-mono"
                    placeholder={"## What to build\n...\n\n## Acceptance criteria\n- \n- \n\n## Background\n..."}
                    value={brief}
                    onChange={(e) => setBrief(e.target.value)}
                    disabled={fireStatus === "loading"}
                  />
                  <p className="text-xs text-muted-foreground">
                    Markdown supported. Write as much as you need — no size limit.
                    This becomes the ⚡ HiC Directive at the top of every agent&apos;s context.
                  </p>
                </div>

                {/* Participants */}
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    Participants
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {AGENTS.map((agent) => (
                      <button
                        key={agent.id}
                        type="button"
                        onClick={() => agent.available && toggleAgent(agent.id)}
                        disabled={!agent.available || fireStatus === "loading"}
                        className={[
                          "flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm font-medium transition-colors",
                          !agent.available
                            ? "opacity-40 cursor-not-allowed border-muted text-muted-foreground"
                            : selectedAgents.includes(agent.id)
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-input hover:bg-accent hover:text-accent-foreground",
                        ].join(" ")}
                      >
                        {agent.label}
                        <span className="text-xs opacity-70">/ {agent.role}</span>
                        {!agent.available && (
                          <span className="text-xs ml-0.5">(paused)</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Meeting Type */}
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Meeting Type</label>
                  <select
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    value={meetingType}
                    onChange={(e) => setMeetingType(e.target.value)}
                    disabled={fireStatus === "loading"}
                  >
                    {MEETING_TYPES.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            ) : fireStatus === "success" ? (
              <div className="py-6 space-y-4 text-center">
                <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto" />
                <div>
                  <p className="font-semibold text-lg">Meeting Fired!</p>
                  {fireResult?.meeting_id && (
                    <p className="text-sm text-muted-foreground mt-1">
                      ID: <span className="font-mono">{fireResult.meeting_id}</span>
                    </p>
                  )}
                  {fireResult?.cost_usd != null && (
                    <p className="text-sm text-muted-foreground">
                      Est. cost: <span className="font-mono">${fireResult.cost_usd.toFixed(3)}</span>
                    </p>
                  )}
                </div>
                {fireResult?.report_url && (
                  <a
                    href={fireResult.report_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    View meeting notes on GitHub
                  </a>
                )}
              </div>
            ) : (
              <div className="py-6 space-y-3 text-center">
                <XCircle className="h-12 w-12 text-destructive mx-auto" />
                <div>
                  <p className="font-semibold text-lg">Something went wrong</p>
                  {fireResult?.error && (
                    <p className="text-sm text-muted-foreground mt-1">{fireResult.error}</p>
                  )}
                </div>
              </div>
            )}

            <DialogFooter className="gap-2 pt-2">
              {fireStatus === "success" || fireStatus === "error" ? (
                <>
                  <Button variant="outline" onClick={resetDialog}>Try Again</Button>
                  <DialogClose asChild>
                    <Button variant="secondary">Close</Button>
                  </DialogClose>
                </>
              ) : (
                <>
                  <DialogClose asChild>
                    <Button variant="outline" disabled={fireStatus === "loading"}>Cancel</Button>
                  </DialogClose>
                  <Button
                    onClick={handleFireMeeting}
                    disabled={
                      fireStatus === "loading" ||
                      (!goal.trim() && !brief.trim()) ||
                      selectedAgents.length === 0
                    }
                    className="min-w-[120px]"
                  >
                    {fireStatus === "loading" ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Firing...
                      </>
                    ) : (
                      <>
                        <Zap className="mr-2 h-4 w-4" />
                        Fire Meeting
                      </>
                    )}
                  </Button>
                </>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Legacy: n8n Control Center */}
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

        {/* System Status */}
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
