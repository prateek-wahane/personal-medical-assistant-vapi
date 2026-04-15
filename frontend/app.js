const apiBase = "http://localhost:8000";

document.getElementById("uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const response = await fetch(`${apiBase}/api/reports/upload`, {
    method: "POST",
    body: form,
  });
  const data = await response.json();
  document.getElementById("uploadResult").textContent = JSON.stringify(data, null, 2);
});

document.getElementById("compareBtn").addEventListener("click", async () => {
  const reportA = document.getElementById("reportA").value.trim();
  const reportB = document.getElementById("reportB").value.trim();
  const response = await fetch(`${apiBase}/api/reports/compare`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ report_id_a: reportA, report_id_b: reportB }),
  });
  const data = await response.json();
  document.getElementById("compareResult").textContent = JSON.stringify(data, null, 2);
});

document.getElementById("mountWidgetBtn").addEventListener("click", () => {
  const assistant = document.getElementById("assistantId").value.trim();
  const apiKey = document.getElementById("publicKey").value.trim();
  const notice = document.getElementById("vapiWidgetNotice");

  if (!assistant || !apiKey) {
    notice.textContent = "Enter both the assistant id and the public key.";
    return;
  }

  const script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js";
  script.defer = true;
  script.async = true;

  script.onload = function () {
    window.vapiSDK.run({
      apiKey,
      assistant,
      config: {
        position: "bottom-right",
        theme: "dark",
      },
    });
    notice.textContent = "Vapi widget mounted.";
  };

  document.body.appendChild(script);
});
