

export async function sendToOpenAI(messages: { role: string; content: string }[]) {
  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages,
    }),
  });

  if (!res.ok) {
    throw new Error("Backend error");
  }

  const data = await res.json();
  return data.choices?.[0]?.message?.content as string;
}
