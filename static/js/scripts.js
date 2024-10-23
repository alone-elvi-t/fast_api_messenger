// Обработка формы входа
$(document).ready(function() {
    $('#login-form').submit(function(event) {
        event.preventDefault();
        
        const credentials = {
            username: $('#username').val(),
            password: $('#password').val()
        };
        
        // Логируем данные перед отправкой
        console.log('Отправляем данные:', {
            url: '/auth/login/',
            method: 'POST',
            contentType: 'application/json',
            data: credentials,
            jsonData: JSON.stringify(credentials)
        });
        
        $.ajax({
            url: '/auth/login/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(credentials),
            success: function(response) {
                window.location.href = '/chat/chat/';
            },
            error: function(xhr) {
                alert('Ошибка авторизации: ' + (xhr.responseJSON?.detail || 'Неизвестная ошибка'));
            }
        });
    });
});

// Определяем функи до их использования
function updateRecipientList() {
    console.log('Запрос списка пользователей...');
    
    $.ajax({
        url: '/chat/users/list',  // Исправленный URL
        method: 'GET',
        success: function(users) {
            console.log('Получен список пользователей:', users);
            const recipientSelect = $('#recipient-select');
            const currentUser = localStorage.getItem('username');
            
            recipientSelect.empty();
            recipientSelect.append($('<option value="">Выберите получателя</option>'));
            
            users.forEach(function(user) {
                if (user !== currentUser) {
                    recipientSelect.append($(`<option value="${user}">${user}</option>`));
                }
            });
            console.log('Список пользователей обновлен');
        },
        error: function(xhr, status, error) {
            console.error('Ошибка получения списка пользователей:');
            console.error('Статус:', status);
            console.error('Ответ сервера:', xhr.responseText);
        }
    });
}

// Глобальная переменная для WebSocket
let ws = null;

// Функция для установки WebSocket соединения
function connectWebSocket(username) {
    ws = new WebSocket(`ws://localhost:8100/websocket/ws/${username}`);
    
    ws.onopen = function() {
        console.log('WebSocket подключен');
        updateRecipientList();  // Обновляем список сразу после подключения
    };
    
    ws.onmessage = function(event) {
        console.log('=== НАЧАЛО ОБРАБОТКИ СООБЩЕНИЯ ===');
        console.log('Получено сообщение:', event.data);
        const chatWindow = $('#chat-window');
        
        try {
            const data = JSON.parse(event.data);
            console.log('Разобранное JSON сообщение:', data);
            console.log('Тип сообщения:', data.type);
            console.log('Проверка условия:', data.type === "history");
            
            if (data.type === "history") {
                console.log('Начинаем обработку истории');
                console.log('Количество сообщений:', data.messages.length);
                
                // Очищаем чат и добавляем заголовок
                chatWindow.html('<p class="text-info">История сообщений:</p>');
                
                // Добавляем каждое сообщение
                data.messages.forEach((msg, index) => {
                    console.log(`Добавляем сообщение ${index}:`, msg);
                    const messageElement = $('<p></p>')
                        .addClass('message')
                        .text(msg)
                        .css({
                            'padding': '8px',
                            'margin': '4px 0',
                            'background-color': '#f8f9fa',
                            'border-radius': '4px',
                            'border': '1px solid #dee2e6'
                        });
                    chatWindow.append(messageElement);
                });
                
                console.log('История сообщений добавлена');
            } else {
                console.log('Обычное сообщение:', data);
                chatWindow.append($('<p></p>').text(data.message));
            }
            
            // Прокручиваем чат вниз
            chatWindow.scrollTop(chatWindow[0].scrollHeight);
        } catch (e) {
            console.error('Ошибка обработки сообщения:', e);
            console.error('Исходное сообщение:', event.data);
            chatWindow.append($('<p class="error"></p>').text(event.data));
        }
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket ошибка:', error);
    };
    
    ws.onclose = function() {
        console.log('WebSocket соединение закрыто');
    };
}

// Инициализация WebSocket при загрузке страницы
$(document).ready(function() {
    const username = localStorage.getItem('username');
    if (username) {
        connectWebSocket(username);
    }
});

// Проверка подключения
function checkConnection() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket состояние:', ws ? ws.readyState : 'не определено');
        return false;
    }
    return true;
}

// Обрабока отправки сообщений
$('#message-form').submit(function(event) {
    event.preventDefault();
    
    const message = $('#message').val().trim();
    
    // Проверяем подключение
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket не подключен');
        alert('Ошибка подключения к серверу');
        return;
    }

    // Проверяем, является ли сообщение командой
    if (message.startsWith('/')) {
        console.log('Отправка команды:', message);
        try {
            ws.send(message);  // Отправляем команду напрямую
            $('#message').val('');
            return;  // Важно! Прерываем выполнение после отправки команды
        } catch (error) {
            console.error('Ошибка отправки команды:', error);
            alert('Ошибка при отправке команды');
            return;
        }
    }

    // Если эт не команда, проверяем получателя
    const recipient = $('#recipient-select').val();
    if (!recipient) {
        alert('Выберите получателя');
        return;
    }

    // Отравка обычного сообщения
    const formattedMessage = `${recipient}:${message}`;
    console.log('Отправка обычного сообщения:', formattedMessage);
    
    try {
        ws.send(formattedMessage);
        $('#message').val('');
        updateRecipientList();
    } catch (error) {
        console.error('Ошибка отправки:', error);
        alert('Ошибка при отправке сообщения');
    }
});

// Добавляем функцию обновления списка пользователей
function updateUsersList(users) {
    const recipientSelect = $('#recipient-select');
    const currentUser = localStorage.getItem('username');
    
    recipientSelect.empty();
    recipientSelect.append($('<option value="">Выберите получателя</option>'));
    
    users.forEach(function(user) {
        if (user !== currentUser) {
            recipientSelect.append($(`<option value="${user}">${user}</option>`));
        }
    });
}

// Обновляем список каждые 30 секунд
setInterval(updateRecipientList, 30000);

// Добавляем обработчики для форм авторизации и регистрации
$(document).ready(function() {
    // Обработка формы регистрации
    $('#register-form').submit(function(event) {
        event.preventDefault();
        
        const userData = {
            username: $('#username').val(),
            password: $('#password').val()
        };
        
        $.ajax({
            url: '/auth/register/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(userData),
            success: function(response) {
                alert('Регистрация успешна!');
                window.location.href = '/auth/login/';
            },
            error: function(xhr) {
                alert('Ошибка регистрации: ' + (xhr.responseJSON?.detail || 'Неизвестная ошибка'));
            }
        });
    });
});

// Очищаем интервал при закрытии страницы
$(window).on('unload', function() {
    clearInterval(updateInterval);
});
