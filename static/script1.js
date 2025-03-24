const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function addMessage(text, sender) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message', sender);
  // \n karakterlerini <br> etiketine dönüştürelim
  const safeText = text.replace(/\n/g, '<br>');
  messageDiv.innerHTML = safeText;
  chatWindow.appendChild(messageDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
  const message = userInput.value.trim();
  if (message) {
    addMessage(message, 'user');
    userInput.value = '';

    try {
      const response = await fetch('http://127.0.0.1:8000/chat/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      if (!response.ok) throw new Error(`HTTP Hatası: ${response.status}`);
      
      // API'den gelen yanıtı JSON'a çevirip konsola yazdırıyoruz
      const data = await response.json();
      console.log("API’den gelen yanıt:", data);
      
      addMessage(data.response || "Bağlantı hatası!", 'bot');
      if (data.response.includes("📅")) {
        sendToCalendar(data.response);
      }
    } catch (error) {
      addMessage("Bağlantı hatası!", 'bot');
      console.error(error);
    }
  }
}

function sendToCalendar(message) {
  window.parent.postMessage({ type: "chatbot_event", message: message }, "*");
}

window.addEventListener("message", (event) => {
  if (event.data.type === "calendar_event") {
    addMessage(event.data.message, "bot");
  }
});

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});
