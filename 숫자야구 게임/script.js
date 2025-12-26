let attempt = 9;
let answer = [];

const input1 = document.getElementById('number1');
const input2 = document.getElementById('number2');
const input3 = document.getElementById('number3');
const submitBtn = document.querySelector('.submit-button');
const resultDisplay = document.querySelector('.result-display');
const resultImg = document.getElementById('game-result-img');
const attemptsSpan = document.getElementById('attempts');

function initializeGame() {
    attempt = 9;
    answer = [];
    
    while (answer.length < 3) {
        let num = Math.floor(Math.random() * 10);
        if (!answer.includes(num)) {
            answer.push(num);
        }
    }
    
    console.log("정답:", answer); 

    input1.value = '';
    input2.value = '';
    input3.value = '';
    
    resultDisplay.innerHTML = ''; 
    resultImg.src = ''; 
    
    attemptsSpan.innerText = attempt;
    submitBtn.disabled = false;
    
    input1.focus();
}

function check_numbers() {
    const val1 = input1.value;
    const val2 = input2.value;
    const val3 = input3.value;

    if (val1 === '' || val2 === '' || val3 === '') {
        input1.value = '';
        input2.value = '';
        input3.value = '';
        input1.focus();
        return;
    }

    const inputNumbers = [parseInt(val1), parseInt(val2), parseInt(val3)];

    let strike = 0;
    let ball = 0;

    for (let i = 0; i < 3; i++) {
        if (answer.includes(inputNumbers[i])) {
            if (inputNumbers[i] === answer[i]) {
                strike++;
            } else {
                ball++;
            }
        }
    }

    const resultRow = document.createElement('div');
    resultRow.className = 'check-result';

    const leftDiv = document.createElement('div');
    leftDiv.className = 'left';
    leftDiv.innerText = `${val1} ${val2} ${val3}`;

    const middleDiv = document.createElement('div');
    middleDiv.innerText = ':';
    middleDiv.style.fontWeight = 'bold';
    middleDiv.style.margin = '0 10px';

    const rightDiv = document.createElement('div');
    rightDiv.className = 'right';

    if (strike === 0 && ball === 0) {
        rightDiv.innerHTML = `<span class="num-result out">O</span>`;
    } else {
        rightDiv.innerHTML = `
            ${strike} <span class="num-result strike">S</span>
            ${ball} <span class="num-result ball">B</span>
        `;
    }

    resultRow.appendChild(leftDiv);
    resultRow.appendChild(middleDiv);
    resultRow.appendChild(rightDiv);

    resultDisplay.appendChild(resultRow);
    resultDisplay.scrollTop = resultDisplay.scrollHeight;

    if (strike === 3) {
        resultImg.src = 'success.png';
        submitBtn.disabled = true;
        return;
    }

    attempt--;
    attemptsSpan.innerText = attempt;

    if (attempt === 0) {
        resultImg.src = 'fail.png';
        submitBtn.disabled = true;
    }
    
    input1.value = '';
    input2.value = '';
    input3.value = '';
    input1.focus();
}

[input1, input2, input3].forEach(input => {
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            check_numbers();
        }
    });
});

initializeGame();