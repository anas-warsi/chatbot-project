async function sendMessage() {
    const inputElem = document.getElementById("userInput");
    const chatDiv = document.getElementById("chatMessages"); // match your HTML ID
    const userMessage = inputElem.value.trim();
    if (!userMessage) return;

    // Add user message
    addMessage("user", userMessage);

    // Clear input
    inputElem.value = "";

    try {
        const response = await fetch("https://chatbot-project-5-fj71.onrender.com/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage }),
        });

        const result = await response.json();
        const botMessage = result?.response || result?.error || "No response";

        // Add bot message
        addMessage("bot", botMessage);

    } catch (err) {
        addMessage("error", "Network error: " + err);
    }
}

// Helper function to add message to chat
function addMessage(type, text) {
    const chatDiv = document.getElementById("chatMessages");
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${type}`;
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    contentDiv.textContent = text;
    msgDiv.appendChild(contentDiv);
    chatDiv.appendChild(msgDiv);

    // Scroll to bottom
    chatDiv.scrollTop = chatDiv.scrollHeight;
}

// Allow Enter key to send
document.getElementById("userInput").addEventListener("keypress", function(event) {
    if (event.key === "Enter") sendMessage();
});
