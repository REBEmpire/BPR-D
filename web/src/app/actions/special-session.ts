'use server';

export async function triggerSpecialSession(formData: FormData) {
  const topic = formData.get('topic') as string;

  if (!topic) {
    return { error: 'Topic is required' };
  }

  const apiKey = process.env.BPRD_API_KEY;
  const meetingsUrl = process.env.BPRD_MEETINGS_URL || 'https://bprd-meetings.onrender.com';

  if (!apiKey) {
    console.error('BPRD_API_KEY not configured on web server');
    return { error: 'Server configuration error' };
  }

  try {
    const res = await fetch(`${meetingsUrl}/api/v1/trigger-special-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-KEY': apiKey,
      },
      body: JSON.stringify({
        topic,
        hic_id: 'russell'
      }),
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
