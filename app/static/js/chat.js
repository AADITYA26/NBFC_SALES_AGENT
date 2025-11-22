document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const userMsg = input.value.trim();
  if (!userMsg) return;

  appendMessage("user", userMsg);
  input.value = "";

  const res = await fetch("/send_message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMsg }),
  });

  const data = await res.json();
  appendMessage("agent", data.response);
}

function appendMessage(role, text) {
  const chatBox = document.getElementById("chat-box");
  const msgDiv = document.createElement("div");
  msgDiv.className = role === "user" ? "user-msg" : "agent-msg";
  msgDiv.textContent = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function loadHistory() {
  const chatBox = document.getElementById("chat-box");
  const res = await fetch("/get_history");
  const data = await res.json();
  data.history.forEach((msg) => {
    appendMessage(msg.role, msg.message);
  });
}
