// function showSuccessMessage(message) {
//     const alertBox = document.createElement('div');
//     alertBox.className = 'alert alert-success';
//     alertBox.innerHTML = message;
//     document.body.prepend(alertBox);
//     setTimeout(() => alertBox.remove(), 3000);  // Уведомление исчезнет через 3 секунды
// }

// let username = "{{ current_user.username }}";
// let socket = new WebSocket(`ws://localhost:8000/ws/${username}`);

// // Получение сообщений с сервера
// socket.onmessage = function (event) {
//     let message = event.data;
//     console.log("Получено сообщение: ", message);
// };

// // Отправка сообщения на сервер
// function sendMessage(recipient, message) {
//     socket.send(`${recipient}:${message}`);
// }

// // Пример использования
// sendMessage("friend_username", "Привет!");

$(document).ready(function () {
    // Логика для страницы выхода
    $('#logout').click(function (event) {
        event.preventDefault();
        // Удаляем токен и перенаправляем на страницу входа
        localStorage.removeItem('token');
        window.location.href = '/auth/login/';
    });

    // Логика для регистрации
    $('#register-form').submit(function (event) {
        event.preventDefault();
        const username = $('#username').val();
        const password = $('#password').val();

        $.ajax({
            url: '/auth/register/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function (response) {
                alert('Пользователь зарегистрирован. Теперь вы можете войти.');
                window.location.href = '/auth/login/';
            }
        });
    });

    // Логика для входа
    $('#login-form').submit(function (event) {
        event.preventDefault();
        const username = $('#username').val();
        const password = $('#password').val();
        debugger;
        $.ajax({
            url: '/auth/login/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            
            success: function (response) {
                localStorage.setItem('token', response.access_token);
                alert('Вы вошли в систему');
                window.location.href = '/chat/chat/';
            },
            error: function () {
                console.log(data)
                alert('Ошибка входа. Проверьте правильность данных.');
            }
        });
    });

    // Логика для чата
    const ws = new WebSocket('ws://localhost:8000//websocket/ws/');
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

