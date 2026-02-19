'use server';

export async function getMonthlyUsage() {
  const meetingsUrl = process.env.BPRD_MEETINGS_URL;
  const apiKey = process.env.BPRD_API_KEY;

  if (!meetingsUrl) {
    console.error("❌ BPRD_MEETINGS_URL not configured");
    return { success: false, message: "Configuration error: BPRD_MEETINGS_URL missing" };
  }

  const baseUrl = meetingsUrl.endsWith('/') ? meetingsUrl.slice(0, -1) : meetingsUrl;
  const upstreamUrl = `${baseUrl}/api/v1/cost/monthly`;

  try {
    // The endpoint is public in main.py, but we include API key if available
    const res = await fetch(upstreamUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...(apiKey ? { "X-API-KEY": apiKey } : {}),
      },
      next: { revalidate: 60 } // Cache for 1 minute
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Upstream error (${res.status}): ${text}`);
    }

    const data = await res.json();
    return { success: true, data };

  } catch (error: any) {
    console.error("❌ Failed to fetch usage:", error);
    return { success: false, message: error.message };
  }
}
