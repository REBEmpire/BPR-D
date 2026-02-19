'use server';

export async function assembleTheCrew(formData: FormData) {
  const task = formData.get('task') as string;
  const successCriteria = formData.get('successCriteria') as string;

  console.log('🚀 Assembling full crew for task:', task);
  console.log('Success criteria:', successCriteria);

  const meetingsUrl = process.env.BPRD_MEETINGS_URL;
  const apiKey = process.env.BPRD_API_KEY;

  if (!meetingsUrl) {
    console.error("❌ BPRD_MEETINGS_URL not configured");
    return { success: false, message: "Configuration error: BPRD_MEETINGS_URL missing" };
  }

  // Ensure no double slash if env var has trailing slash
  const baseUrl = meetingsUrl.endsWith('/') ? meetingsUrl.slice(0, -1) : meetingsUrl;
  const upstreamUrl = `${baseUrl}/api/v1/meetings/manual-trigger`;

  const upstreamBody = {
    meeting_type: "work_session",
    participants: ["grok", "claude", "gemini", "abacus"],
    goal: successCriteria || "Team assembly requested via manual trigger",
    custom_prompt: task ? `Task: ${task}\n\nSuccess Criteria: ${successCriteria}` : undefined
  };

  try {
    const upstreamRes = await fetch(upstreamUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(apiKey ? { "X-API-KEY": apiKey } : {}),
      },
      body: JSON.stringify(upstreamBody),
    });

    if (!upstreamRes.ok) {
        const text = await upstreamRes.text();
        console.error(`❌ Upstream failed (${upstreamRes.status}):`, text);
        return { success: false, message: `Upstream error: ${text}` };
    }

    const data = await upstreamRes.json();
    console.log("✅ Upstream success:", data);
    return { success: true, task, data };

  } catch (error: any) {
    console.error("❌ Assemble crew failed:", error);
    return { success: false, message: error.message };
  }
}
