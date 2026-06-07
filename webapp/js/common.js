const tg = window.Telegram?.WebApp;

function initTelegramApp() {
  if (!tg) return;
  tg.ready();
  tg.expand();
  document.documentElement.setAttribute("data-theme", "dark");
  if (tg.themeParams?.bg_color) {
    document.body.style.backgroundColor = tg.themeParams.bg_color;
  }
  const user = tg.initDataUnsafe?.user;
  if (user?.username) {
    const input = document.querySelector("[name=username]");
    if (input && !input.value) input.value = user.username;
  }
}

function getInitData() {
  return tg?.initData || "";
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": getInitData(),
    },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data.ok) {
    throw new Error(data.error || `HTTP ${res.status}`);
  }
  return data;
}

function showStatus(el, message, type = "info") {
  if (!el) return;
  el.classList.remove("hidden", "alert-info", "alert-success", "alert-error");
  el.classList.add(
    type === "success" ? "alert-success" : type === "error" ? "alert-error" : "alert-info"
  );
  el.textContent = message;
}

function closeApp() {
  tg?.close();
}

document.addEventListener("DOMContentLoaded", initTelegramApp);
