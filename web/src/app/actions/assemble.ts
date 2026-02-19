'use server';

export async function assembleTheCrew(formData: FormData) {
  const task = formData.get('task') as string;
  const successCriteria = formData.get('successCriteria') as string;

  // ←←← YOUR REAL ORCHESTRATION GOES HERE (real xAI multi-agent call)
  console.log('🚀 Assembling full crew for task:', task);
  console.log('Success criteria:', successCriteria);

  // Example real call (replace with your actual endpoint / xAI SDK)
  // const response = await fetch('/api/assemble-crew', {
  //   method: 'POST',
  //   body: JSON.stringify({ task, successCriteria }),
  // });

  // For now this prevents the error and logs — we will wire full crew launch next commit
  return { success: true, task };
}
