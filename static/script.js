document.addEventListener("DOMContentLoaded", () => {
  const calendarContainer = document.getElementById("days");
  const agenda = document.getElementById("agenda");
  const agendaTitle = document.getElementById("agenda-title");
  const hourlyAgenda = document.getElementById("hourly-agenda");
  const closeAgenda = document.getElementById("close-agenda");
  const prevMonth = document.getElementById("prev-month");
  const nextMonth = document.getElementById("next-month");
  const monthDisplay = document.getElementById("current-month");
  const chatButton = document.getElementById("chat-button");
  const chatIframe = document.getElementById("chatbot-iframe");

  let currentDate = new Date();
  renderCalendar();

  closeAgenda.addEventListener("click", () => {
    agenda.style.display = "none";
  });

  prevMonth.addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
  });
  nextMonth.addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
  });

  chatButton.addEventListener("click", () => {
    chatIframe.style.display =
      (chatIframe.style.display === "none" || !chatIframe.style.display)
        ? "block" : "none";
    if (chatIframe.style.display === "block") {
      chatIframe.src = "/static/index1.html";
    }
  });

  window.addEventListener("message", (event) => {
    if (event.data.type === "chatbot_event") {
      alert("Chatbot yeni bir etkinlik önerdi: " + event.data.message);
    }
  });

  function renderCalendar() {
    calendarContainer.innerHTML = "";
    let firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
    firstDay = (firstDay === 0) ? 7 : firstDay;
    firstDay--;
    const lastDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
    monthDisplay.innerText = currentDate.toLocaleDateString("tr-TR", { month: "long", year: "numeric" });
    for (let i = 0; i < firstDay; i++) {
      const emptyDiv = document.createElement("div");
      emptyDiv.classList.add("empty");
      calendarContainer.appendChild(emptyDiv);
    }
    for (let day = 1; day <= lastDate; day++) {
      const dayElement = document.createElement("div");
      dayElement.className = "day";
      dayElement.textContent = day;
      dayElement.addEventListener("click", () => showAgenda(day));
      const dateString = formatDate(currentDate.getFullYear(), currentDate.getMonth() + 1, day);
      checkEventForDay(dateString, dayElement);
      calendarContainer.appendChild(dayElement);
    }
  }

  function formatDate(year, month, day) {
    const mm = String(month).padStart(2, '0');
    const dd = String(day).padStart(2, '0');
    return `${year}-${mm}-${dd}`;
  }

  function checkEventForDay(dateString, dayElement) {
    fetch(`http://127.0.0.1:8000/events/${dateString}`)
      .then(res => res.json())
      .then(data => {
        if (data.length > 0) {
          dayElement.classList.add("has-event");
        }
      })
      .catch(err => console.error("Gün etkinliği sorgu hatası:", err));
  }

  function showAgenda(day) {
    agenda.style.display = "block";
    agendaTitle.textContent = `${day} ${currentDate.toLocaleDateString("tr-TR", { month: "long" })} Ajanda`;
    hourlyAgenda.innerHTML = "";
    const dateString = formatDate(currentDate.getFullYear(), currentDate.getMonth() + 1, day);
    fetch(`http://127.0.0.1:8000/events/${dateString}`)
      .then(res => res.json())
      .then(eventsList => {
        if (eventsList.length === 0) {
          const msg = document.createElement("p");
          msg.textContent = "Bu tarihte etkinlik yok!";
          hourlyAgenda.appendChild(msg);
        } else {
          eventsList.forEach(evt => {
            const hourDiv = document.createElement("div");
            hourDiv.className = "hour";
            hourDiv.innerHTML = `
              <span>${evt.start_time}</span>
              <p class="event-text">${evt.name}</p>
              <button class="del-btn" data-id="${evt.id}">Sil</button>
            `;
            hourlyAgenda.appendChild(hourDiv);
            hourDiv.querySelector(".del-btn").addEventListener("click", () => {
              deleteEvent(evt.id, day);
            });
          });
        }
        const addBtn = document.createElement("button");
        addBtn.textContent = "Yeni Etkinlik Ekle";
        addBtn.addEventListener("click", () => addEventToDB(dateString, day));
        hourlyAgenda.appendChild(addBtn);
      })
      .catch(err => {
        console.error(err);
        hourlyAgenda.innerHTML = "<p>Etkinlikler alınırken hata oluştu!</p>";
      });
  }

  function deleteEvent(eventId, day) {
    fetch(`http://127.0.0.1:8000/events/delete/${eventId}`, {
      method: "DELETE"
    })
      .then(res => {
        if (!res.ok) throw new Error("Silme hatası");
        showAgenda(day);
        renderCalendar();
      })
      .catch(err => console.error(err));
  }

  function addEventToDB(dateString, day) {
    const eventName = prompt("Etkinlik adı girin:");
    if (!eventName) return;
    const startTime = prompt("Başlangıç saati (HH:MM)", "10:00");
    fetch("http://127.0.0.1:8000/events/add_event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: eventName,
        date: dateString,
        start_time: startTime
      })
    })
      .then(res => res.json())
      .then(data => {
        alert(data.message || "Etkinlik eklendi!");
        showAgenda(day);
        renderCalendar();
      })
      .catch(err => {
        console.error("Etkinlik eklenirken hata:", err);
        alert("Etkinlik ekleme başarısız!");
      });
  }
});
