async function sendMessage() {
  const input = document.getElementById("userInput").value;
  if (!input) return;

  const chatDiv = document.getElementById("chat");
  chatDiv.innerHTML += `<p><strong>You:</strong> ${input}</p>`;

  try {
    const response = await fetch("https://chatbot-project-5-fj71.onrender.com/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }), // <-- key must be "message"
    });

    const result = await response.json();
    const botMessage = result?.response || "No response"; // <-- access "response"
    chatDiv.innerHTML += `<p><strong>Bot:</strong> ${botMessage}</p>`;
  } catch (err) {
    chatDiv.innerHTML += `<p style="color:red;">Error: ${err}</p>`;
  }

  document.getElementById("userInput").value = "";
}
