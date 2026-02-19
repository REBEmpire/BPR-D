import { NextRequest, NextResponse } from "next/server";

// Force full registration on Render + Turbopack
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    route: "/api/hic/trigger",
    message: "Route live — POST ready",
    timestamp: new Date().toISOString(),
  });
}

export async function POST(request: NextRequest) {
  console.log("🔥 [TRIGGER] POST received at", new Date().toISOString());

  try {
    let task: string | null = null;
    let successCriteria: string | null = null;
    let payload: any = {};

    // 1. Try FormData (original form buttons)
    const contentType = request.headers.get("content-type") || "";

    if (contentType.includes("multipart/form-data") || contentType.includes("application/x-www-form-urlencoded")) {
      console.log("📋 Processing as FormData (Content-Type: " + contentType + ")");
      try {
        const formData = await request.formData();
        task = formData.get("task") as string;
        successCriteria = formData.get("successCriteria") as string || formData.get("goal") as string;
        console.log("✅ FormData parsed successfully");
      } catch (e: any) {
        console.error("⚠️ FormData parsing failed:", e.message);
        // Fallback or error? If it claims to be form data but fails, it's likely broken.
        // We can't really try JSON if the stream was consumed.
      }
    } else {
      // 2. Try JSON (common fetch calls, or missing content-type)
      console.log("📦 Processing as JSON (Content-Type: " + contentType + ")");
      try {
        payload = await request.json();
        task = payload.task || payload.meeting_type;
        successCriteria = payload.successCriteria || payload.goal || payload.custom_prompt;
        console.log("✅ JSON parsed successfully");
      } catch (e: any) {
         console.warn("⚠️ JSON parsing failed or body empty:", e.message);
         // If json fails, payload is empty, task is null.
      }
    }

    console.log("✅ Extracted → Task:", task);
    console.log("✅ Extracted → Criteria/Goal:", successCriteria);

    // Real Upstream Call
    const meetingsUrl = process.env.BPRD_MEETINGS_URL;
    const apiKey = process.env.BPRD_API_KEY;

    if (!meetingsUrl) {
       console.error("❌ BPRD_MEETINGS_URL not configured");
       return NextResponse.json({
         success: false,
         message: "Configuration error: BPRD_MEETINGS_URL missing"
       }, { status: 500 });
    }

    // Construct upstream URL
    // Ensure no double slash if env var has trailing slash
    const baseUrl = meetingsUrl.endsWith('/') ? meetingsUrl.slice(0, -1) : meetingsUrl;
    const upstreamUrl = `${baseUrl}/api/v1/meetings/manual-trigger`;

    // Construct body for upstream
    // If the original payload already has meeting_type/participants (from AI Comm Hub form),
    // forward those directly. Otherwise build from extracted fields (legacy form buttons).
    const upstreamBody = payload.meeting_type
      ? {
          meeting_type: payload.meeting_type,
          participants: payload.participants || ["grok", "claude", "gemini", "abacus"],
          goal: payload.goal || successCriteria || "Team assembly requested via manual trigger",
          custom_prompt: payload.custom_prompt || (task ? `Task: ${task}\n\nSuccess Criteria: ${successCriteria}` : undefined),
        }
      : {
          meeting_type: "daily_briefing",
          participants: ["grok", "claude", "gemini", "abacus"],
          goal: successCriteria || "Team assembly requested via manual trigger",
          custom_prompt: task ? `Task: ${task}\n\nSuccess Criteria: ${successCriteria}` : undefined,
        };

    console.log("🚀 Forwarding to:", upstreamUrl);
    // console.log("Payload:", JSON.stringify(upstreamBody, null, 2));

    // 30s timeout safety net — backend should respond instantly (fire-and-forget)
    // but if Render is cold-starting or down, don't hang forever.
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30_000);

    let upstreamRes;
    try {
        upstreamRes = await fetch(upstreamUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(apiKey ? { "X-API-KEY": apiKey } : {}),
          },
          body: JSON.stringify(upstreamBody),
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
    } catch (fetchError: any) {
        clearTimeout(timeoutId);
        console.error("❌ Fetch failed:", fetchError.message);
         return NextResponse.json({
            success: false,
            message: fetchError.name === "AbortError"
              ? "Meeting service timed out (30s). It may still be starting up — try again in a moment."
              : "Failed to connect to upstream service",
            error: fetchError.message
        }, { status: 502 });
    }

    if (!upstreamRes.ok) {
        const errorText = await upstreamRes.text();
        console.error(`❌ Upstream failed (${upstreamRes.status}):`, errorText);
        return NextResponse.json({
            success: false,
            message: `Upstream service returned ${upstreamRes.status}`,
            error: errorText
        }, { status: upstreamRes.status });
    }

    const data = await upstreamRes.json();

    console.log("✅ Upstream success:", data);

    return NextResponse.json(data, { status: 200 });

  } catch (error: any) {
    console.error("❌ [TRIGGER] POST crashed:", error.message);
    console.error("❌ Full stack:", error.stack);
    return NextResponse.json({
      success: false,
      message: "Internal trigger error — check Render Logs for full stack",
      error: error.message,
    }, { status: 500 });
  }
}
