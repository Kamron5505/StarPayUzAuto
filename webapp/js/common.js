// StarPayUz - Common JavaScript Functions

const tg = window.Telegram.WebApp;
tg.expand();
tg.ready();
tg.setHeaderColor('#0F1419');
tg.setBackgroundColor('#0F1419');

// User balance
let userBalance = 0;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadUserBalance();
});

// Load user balance
function loadUserBalance() {
    const balanceElement = document.getElementById('balance');
    if (balanceElement) {
        // TODO: Load from server
        userBalance = 0;
        balanceElement.textContent = userBalance.toLocaleString('uz-UZ') + ' so\'m';
    }
}

// Format number with spaces
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

// Show loading
function showLoading() {
    tg.MainButton.showProgress();
}

// Hide loading
function hideLoading() {
    tg.MainButton.hideProgress();
}
