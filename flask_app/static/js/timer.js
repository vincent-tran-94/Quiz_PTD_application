var initialTimer = 300; // 5 minutes
var timer = initialTimer;
var warnings = 0;
let ButtonClicked = false;
var isRedirected = false; // Variable to track if redirection has occurred
var countdown;
var startTime;

// Function to update the progress bar
function updateProgressBar() {
    var progressBar = document.getElementById('progressBar');
    var percentage = ((initialTimer - timer) / initialTimer) * 100;
    progressBar.style.width = percentage + '%';
}

// Function to reduce time by 30 seconds and update UI
function reduceTime() {
    timer -= 30;
    updateProgressBar();
    if (timer <= 0) {
        clearInterval(countdown);
        if (!isRedirected) {
            window.location.href = "{{ url_for('progression') }}"; // Redirect to the progression page
            document.forms["questionnaireForm"].submit(); // Submit the form when time is up
            isRedirected = true; // Mark that the redirection has occurred
        }
    }
}

// Function to handle warnings
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

// Function to save the start time in sessionStorage
function saveStartTime() {
    sessionStorage.setItem('startTime', startTime);
}

// Function to load the timer from sessionStorage (Gestion des cookies)
function loadTimer() {
    var storedStartTime = sessionStorage.getItem('startTime');
    if (storedStartTime !== null) {
        startTime = parseInt(storedStartTime, 10);
        var elapsedTime = Math.floor((Date.now() - startTime) / 1000);
        timer = initialTimer - elapsedTime;
        if (timer <= 0) {
            timer = 0;
        }
    } else {
        startTime = Date.now();
        timer = initialTimer;
    }
}

// Function to handle the end of the timer
function handleTimerEnd() {
    timer = initialTimer; // Reset the timer to the initial value
    sessionStorage.removeItem('startTime'); // Remove the entry from session storage
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
    loadTimer(); // Load the timer from session storage
    updateProgressBar();
    saveStartTime(); // Save the start time in session storage

    countdown = setInterval(function () {
        timer--;
        updateProgressBar();
        if (timer <= 0) {
            clearInterval(countdown);
            handleTimerEnd();
        }
    }, 1000); // Update every second

    // Add event listener to the form to clear the timer only if submit button is clicked
    document.getElementById('questionnaireForm').addEventListener('submit', function(event) {
        if (document.activeElement && document.activeElement.id === 'submitButton') {
            sessionStorage.removeItem('startTime');
        }
    });
});
