let currentWord = ''; // Текущее слово

// Функция для добавления буквы в слово
function addLetter(letter) {
    currentWord += letter; // Добавляем букву к текущему слову
    document.getElementById('input-field').value = currentWord; // Обновляем поле ввода
}

// Функция для обновления текущего слова при изменении текста в поле ввода
function updateWord() {
    currentWord = document.getElementById('input-field').value; // Обновляем текущее слово
}

// Функция для удаления последнего символа
function deleteLetter() {
    currentWord = currentWord.slice(0, -1); // Удаляем последний символ
    document.getElementById('input-field').value = currentWord; // Обновляем поле ввода
}

// Функция для проверки слова (заглушка)
function checkWord() {
    // Логика для проверки правильности слова
    // Здесь можно добавить проверку, но пока просто заглушка
    alert('Проверка слова: ' + currentWord);
}

// Функция для начала игры и отсчета времени
function startGame() {
    let timeLeft = 60;
    const timerDisplay = document.getElementById('timer');
    const startButton = document.getElementById('start-btn');
    
    // Скрыть кнопку "Начать игру" после нажатия
    startButton.style.display = 'none';
    
    // Обновляем таймер каждую секунду
    const timerInterval = setInterval(function() {
        timeLeft--;
        timerDisplay.textContent = timeLeft;
        
        // Если время закончилось, останавливаем таймер и перезагружаем страницу
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            alert('Время вышло!');
            location.reload(); // Перезагружаем страницу
        }
    }, 1000); // 1000 миллисекунд = 1 секунда
}
// Скрипт для переключения подсказок
const toggle = document.getElementById('tips-toggle');
const statusText = document.getElementById('tips-status');

toggle.addEventListener('change', function() {
    if (toggle.checked) {
        statusText.textContent = 'Подсказки включены.';
    } else {
        statusText.textContent = 'Подсказки выключены.';
    }
});