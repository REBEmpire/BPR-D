import { NextRequest, NextResponse } from "next/server";

// Force full registration on Render + Turbopack
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    route: "/api/hic/trigger",
    message: "Route live — POST ready (Fire Team → special_session)",
    timestamp: new Date().toISOString(),
  });
}

export async function POST(request: NextRequest) {
  console.log("[TRIGGER] POST received at", new Date().toISOString());

  try {
    const payload = await request.json();

    const topic = payload.topic;
    const participants = payload.participants; // array or undefined
    const numRounds = payload.num_rounds;      // number or undefined
    const hicId = payload.hic_id || "russell";

    if (!topic) {
      return NextResponse.json(
        { success: false, message: "Topic is required" },
        { status: 400 }
      );
    }

    console.log(
      `[TRIGGER] topic=${(topic as string).slice(0, 80)}`,
      `participants=${JSON.stringify(participants)}`,
      `num_rounds=${numRounds}`
    );

    // Real Upstream Call → Special Session endpoint
    const meetingsUrl = process.env.BPRD_MEETINGS_URL;
    const apiKey = process.env.BPRD_API_KEY;

    if (!meetingsUrl) {
      console.error("[TRIGGER] BPRD_MEETINGS_URL not configured");
      return NextResponse.json(
        { success: false, message: "Configuration error: BPRD_MEETINGS_URL missing" },
        { status: 500 }
      );
    }

    const baseUrl = meetingsUrl.endsWith("/") ? meetingsUrl.slice(0, -1) : meetingsUrl;
    const upstreamUrl = `${baseUrl}/api/v1/trigger-special-session`;

    // Build upstream body — forward exactly what the special session endpoint expects
    const upstreamBody: Record<string, unknown> = {
      topic,
      hic_id: hicId,
    };
    if (participants && Array.isArray(participants) && participants.length > 0) {
      upstreamBody.participants = participants;
    }
    if (numRounds != null) {
      upstreamBody.num_rounds = numRounds;
    }

    console.log("[TRIGGER] Forwarding to:", upstreamUrl);

    // 30s timeout safety net — backend should respond instantly (fire-and-forget)
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
      console.error("[TRIGGER] Fetch failed:", fetchError.message);
      return NextResponse.json(
        {
          success: false,
          message:
            fetchError.name === "AbortError"
              ? "Meeting service timed out (30s). It may still be starting up — try again in a moment."
              : "Failed to connect to upstream service",
          error: fetchError.message,
        },
        { status: 502 }
      );
    }

    if (!upstreamRes.ok) {
      const errorText = await upstreamRes.text();
      console.error(`[TRIGGER] Upstream failed (${upstreamRes.status}):`, errorText);
      return NextResponse.json(
        {
          success: false,
          message: `Upstream service returned ${upstreamRes.status}`,
          error: errorText,
        },
        { status: upstreamRes.status }
      );
    }

    const data = await upstreamRes.json();
    console.log("[TRIGGER] Upstream success:", data);

    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error("[TRIGGER] POST crashed:", error.message);
    console.error("[TRIGGER] Full stack:", error.stack);
    return NextResponse.json(
      {
        success: false,
        message: "Internal trigger error — check Render Logs for full stack",
        error: error.message,
      },
      { status: 500 }
    );
  }
}
