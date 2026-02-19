import { NextRequest, NextResponse } from "next/server"

/**
 * POST /api/hic/trigger
 *
 * Server-side proxy for the HiC manual team meeting trigger.
 * Forwards to crewai-service, injecting the BPRD_API_KEY server-side
 * so it is never exposed to the browser.
 *
 * Body (passed through):
 *   meeting_type  string   — "daily_briefing" | "work_session" (default: "daily_briefing")
 *   participants  string[] — agent names (default: all four)
 *   goal          string   — short goal description
 *   custom_prompt string   — full brief / rich agenda (optional, overrides goal)
 *
 * Returns:
 *   { status, meeting_id, meeting_type, participants, goal, report_url, cost_usd }
 */
export async function POST(req: NextRequest) {
  const meetingsUrl = process.env.BPRD_MEETINGS_URL
  const apiKey = process.env.BPRD_API_KEY

  if (!meetingsUrl) {
    return NextResponse.json(
      { error: "BPRD_MEETINGS_URL is not configured on this server." },
      { status: 503 }
    )
  }

  let body: Record<string, unknown>
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 })
  }

  const upstreamUrl = `${meetingsUrl.replace(/\/$/, "")}/api/v1/meetings/manual-trigger`

  let upstreamRes: Response
  try {
    upstreamRes = await fetch(upstreamUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(apiKey ? { "X-API-KEY": apiKey } : {}),
      },
      body: JSON.stringify(body),
    })
  } catch (err) {
    console.error("[hic/trigger] Failed to reach crewai-service:", err)
    return NextResponse.json(
      { error: "Could not reach the meeting service. Is it deployed?" },
      { status: 502 }
    )
  }

  const data = await upstreamRes.json().catch(() => ({}))

  return NextResponse.json(data, { status: upstreamRes.status })
}
