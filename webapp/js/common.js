// StarPayUz - Common JavaScript Functions

const STARS_MIN = 50;
const STARS_MAX = 1000000;

const tg = window.Telegram.WebApp;
tg.expand();
tg.ready();
tg.setHeaderColor('#030712');
tg.setBackgroundColor('#030712');

let userBalance = 0;

document.addEventListener('DOMContentLoaded', function () {
    fillUsernameFromTelegram();
    loadUserBalance();
});

function fillUsernameFromTelegram() {
    const input = document.getElementById('username');
    const user = tg.initDataUnsafe?.user;
    if (input && user?.username && !input.value.trim()) {
        input.value = '@' + user.username;
    }
}

function loadUserBalance() {
    const balanceElement = document.getElementById('balance');
    if (balanceElement) {
        userBalance = 0;
        balanceElement.textContent = userBalance.toLocaleString('uz-UZ') + " so'm";
    }
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

function getUsername(inputId) {
    const val = (document.getElementById(inputId || 'username')?.value || '').trim();
    if (!val || val === '@') return null;
    return val.startsWith('@') ? val : '@' + val;
}

function setBuyButtonLoading(btnId, loading) {
    const btn = document.getElementById(btnId || 'buyBtn');
    if (!btn) return;
    if (loading) {
        btn.dataset.originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = 'Yuborilmoqda...';
    } else {
        btn.disabled = false;
        btn.textContent = btn.dataset.originalText || 'Sotib olish';
    }
}

function submitOrder(payload, btnId) {
    setBuyButtonLoading(btnId, true);
    try {
        tg.sendData(JSON.stringify(payload));
        setTimeout(() => tg.close(), 300);
    } catch (e) {
        setBuyButtonLoading(btnId, false);
        tg.showAlert('Xatolik: ' + (e.message || 'qayta urinib ko\'ring'));
    }
}

function validateStarsAmount(amount) {
    const n = parseInt(amount, 10);
    if (isNaN(n) || n < STARS_MIN) {
        return { ok: false, message: `Minimal miqdor: ${STARS_MIN} stars` };
    }
    if (n > STARS_MAX) {
        return { ok: false, message: `Maksimal miqdor: ${STARS_MAX.toLocaleString('uz-UZ')} stars` };
    }
    return { ok: true, value: n };
}
