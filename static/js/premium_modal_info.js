function showModal(period, price) {
    document.getElementById('modalTitle').textContent = 'Премиум на ' + period;
    document.getElementById('modalPrice').textContent = 'Цена: ' + price;
    document.getElementById('paymentPeriod').textContent = period;
    document.getElementById('myModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('myModal').style.display = 'none';
}

// Закрыть модальное окно при клике вне его
window.onclick = function (event) {
    var modal = document.getElementById('myModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}