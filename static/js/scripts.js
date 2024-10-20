// Получаем имя пользователя из localStorage (если оно сохраняется после входа)
const username = localStorage.getItem('username'); // Предполагается, что оно сохраняется при входе

// Подключаем WebSocket с именем пользователя
const ws = new WebSocket(`ws://localhost:8100/websocket/ws/${username}`);

// Логика получения сообщений
ws.onmessage = function (event) {
    const chatWindow = $('#chat-window');
    const newMessage = $('<p></p>').text(event.data);
    chatWindow.append(newMessage);
};

// Логика отправки сообщений
$('#message-form').submit(function (event) {
    event.preventDefault();
    const message = $('#message').val();
    const recipient = prompt("Введите имя получателя:");
    const formattedMessage = `${recipient}:${message}`;  // Форматируем сообщение

    ws.send(formattedMessage);  // Отправляем сообщение через WebSocket
    $('#message').val('');  // Очищаем поле ввода
});


// Логика для входа
$('#login-form').submit(function (event) {
    event.preventDefault();
    const username = $('#username').val();
    const password = $('#password').val();

    $.ajax({
        url: '/auth/login/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ username: username, password: password }),

        success: function (response) {
            localStorage.setItem('token', response.access_token);  // Сохраняем токен
            localStorage.setItem('username', username);  // Сохраняем имя пользователя
            alert('Вы вошли в систему');
            window.location.href = '/chat/chat/';
        },
        error: function () {
            alert('Ошибка входа. Проверьте правильность данных.');
        }
    });
});


// Логика для выхода
$('#logout').click(function (event) {
    event.preventDefault();
    localStorage.removeItem('token');  // Удаляем токен
    localStorage.removeItem('username');  // Удаляем имя пользователя
    window.location.href = '/auth/login/';  // Перенаправляем на страницу входа
});
