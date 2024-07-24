var initialTimer = 600; // 10 minutes
var timer = initialTimer;
var warnings = 0;
let ButtonClicked = false;
var isRedirected = false; // Variable to track if redirection has occurred

function updateProgressBar() {
    var progressBar = document.getElementById('progressBar');
    var percentage = ((initialTimer - timer) / initialTimer) * 100;
    progressBar.style.width = percentage + '%';
}

function reduceTime() {
    timer -= 30;
    updateProgressBar();
    saveTimer();
    if (timer <= 0) {
        clearInterval(countdown);
        if (!isRedirected) {
            window.location.href = "{{ url_for('progression') }}"; // Redirect to the progression page
            document.forms["questionnaireForm"].submit(); // Submit the form when time is up
            isRedirected = true; // Mark that the redirection has occurred
        }
    }
}

function handleWarnings() {
    if (!ButtonClicked && !isRedirected) {
        if (warnings == 1) {
            alert("Attention : Quitter cette page réduira le temps restant.");
        } else if (warnings >= 2) {
            alert("Attention : Vous avez perdu 30 secondes.");
            reduceTime();
        }
    }
}

function saveTimer() {
    localStorage.setItem('remainingTime', timer);
}

function loadTimer() {
    var storedTime = localStorage.getItem('remainingTime');
    if (storedTime !== null && !isNaN(storedTime)) {
        timer = parseInt(storedTime, 10);
    } else {
        timer = initialTimer; // Initialize to 600 seconds (10 minutes) if no value is found
    }
}

function handleTimerEnd() {
    timer = initialTimer; // Reset the timer to the initial value
    localStorage.removeItem('remainingTime'); // Remove the entry from local storage
    if (!isRedirected) {
        alert('Le temps est écoulé. Vous allez être redirigé vers la page des résultats.');
        window.location.href = "{{ url_for('progression') }}"; // Redirect to the progression page
        document.forms["questionnaireForm"].submit(); // Submit the form when time is up
        isRedirected = true; // Mark that the redirection has occurred
    }
}

document.querySelector('.btn.btn-primary.mt-3').addEventListener('click', function() {
    ButtonClicked = true;
});

document.addEventListener('visibilitychange', function () {
    if (!ButtonClicked) {
        handleWarnings();
        warnings++;
    }
});

document.addEventListener('DOMContentLoaded', function () {
    loadTimer(); // Load the timer from local storage
    updateProgressBar();
    var countdown = setInterval(function () {
        timer--;
        updateProgressBar();
        saveTimer();
        if (timer <= 0) {
            clearInterval(countdown);
            handleTimerEnd();
        }
    }, 1000); // Update every second

    // Add event listener to the form to clear the timer only if submit button is clicked
    document.getElementById('questionnaireForm').addEventListener('submit', function(event) {
        if (document.activeElement && document.activeElement.id === 'submitButton') {
            localStorage.removeItem('remainingTime');
        }
    });
});
