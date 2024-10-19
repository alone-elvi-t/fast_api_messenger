$(document).ready(function () {
    // Логика для страницы выхода
    $('#logout').click(function (event) {
        event.preventDefault();
        // Удаляем токен и перенаправляем на страницу входа
        localStorage.removeItem('token');
        window.location.href = '/login';
    });

    // Логика для регистрации
    $('#register-form').submit(function (event) {
        event.preventDefault();
        const username = $('#username').val();
        const password = $('#password').val();

        $.ajax({
            url: '/register/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function (response) {
                alert('Пользователь зарегистрирован. Теперь вы можете войти.');
                window.location.href = '/login';
            }
        });
    });

    // Логика для входа
    $('#login-form').submit(function (event) {
        event.preventDefault();
        const username = $('#username').val();
        const password = $('#password').val();

        $.ajax({
            url: '/login/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function (response) {
                localStorage.setItem('token', response.access_token);
                alert('Вы вошли в систему');
                window.location.href = '/chat';
            },
            error: function () {
                alert('Ошибка входа. Проверьте правильность данных.');
            }
        });
    });

    // Логика для чата
    const ws = new WebSocket('ws://localhost:8000/ws/');
    ws.onmessage = function (event) {
        const chatWindow = $('#chat-window');
        const newMessage = $('<p></p>').text(event.data);
        chatWindow.append(newMessage);
    };

    $('#message-form').submit(function (event) {
        event.preventDefault();
        const message = $('#message').val();
        ws.send(message);
        $('#message').val('');
    });
});
