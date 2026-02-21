'use server';

export async function triggerSpecialSession(formData: FormData) {
  const topic = formData.get('topic') as string;
  const participantsRaw = formData.get('participants') as string | null;
  const numRoundsRaw = formData.get('num_rounds') as string | null;

  if (!topic) {
    return { error: 'Topic is required' };
  }

  const apiKey = process.env.BPRD_API_KEY;
  const meetingsUrl = process.env.BPRD_MEETINGS_URL || 'https://bprd-meetings.onrender.com';

  if (!apiKey) {
    console.error('BPRD_API_KEY not configured on web server');
    return { error: 'Server configuration error' };
  }

  // Parse participants: comma-separated string → array, or null for defaults
  const participants = participantsRaw
    ? participantsRaw.split(',').map((p) => p.trim()).filter(Boolean)
    : undefined;

  // Parse num_rounds: string → number, or undefined for default
  const numRounds = numRoundsRaw ? parseInt(numRoundsRaw, 10) : undefined;

  try {
    const body: Record<string, unknown> = {
      topic,
      hic_id: 'russell',
    };
    if (participants && participants.length > 0) {
      body.participants = participants;
    }
    if (numRounds && numRounds >= 2 && numRounds <= 13) {
      body.num_rounds = numRounds;
    }

    const res = await fetch(`${meetingsUrl}/api/v1/trigger-special-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-KEY': apiKey,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error('Failed to trigger session:', res.status, errorText);
      return { error: `Failed to trigger session: ${res.statusText}` };
    }

    const data = await res.json();
    return { success: true, data };
  } catch (error) {
    console.error('Error triggering special session:', error);
    return { error: 'Network error or service unreachable' };
  }
}
