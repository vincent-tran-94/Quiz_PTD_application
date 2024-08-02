var initialTimer = 600; // 10 minutes
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
    saveTimer();
    updateProgressBar();
    if (timer <= 0) {
        clearInterval(countdown);
        handleTimerEnd();
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

// Function to save the timer in sessionStorage
function saveTimer() {
    sessionStorage.setItem('remainingTime', timer);
    sessionStorage.setItem('lastSaveTime', Date.now());
}

// Function to load the timer from sessionStorage
function loadTimer() {
    var storedTimer = sessionStorage.getItem('remainingTime');
    var lastSaveTime = sessionStorage.getItem('lastSaveTime');
    if (storedTimer !== null && lastSaveTime !== null) {
        var elapsedTime = Math.floor((Date.now() - parseInt(lastSaveTime, 10)) / 1000);
        timer = parseInt(storedTimer, 10) - elapsedTime;
        if (timer <= 0) {
            timer = 0;
        }
    } else {
        timer = initialTimer;
    }
}

// Function to handle the end of the timer
function handleTimerEnd() {
    timer = initialTimer; // Reset the timer to the initial value
    sessionStorage.removeItem('remainingTime'); // Remove the entry from session storage
    sessionStorage.removeItem('lastSaveTime'); // Remove the entry from session storage
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

    countdown = setInterval(function () {
        timer--;
        if (timer <= 0) {
            clearInterval(countdown);
            handleTimerEnd();
        } else {
            saveTimer(); // Save the remaining time in session storage
            updateProgressBar();
        }
    }, 1000); // Update every second

    // Add event listener to the form to clear the timer only if submit button is clicked
    document.getElementById('questionnaireForm').addEventListener('submit', function(event) {
        if (document.activeElement && document.activeElement.id === 'submitButton') {
            sessionStorage.removeItem('remainingTime');
            sessionStorage.removeItem('lastSaveTime');
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('questionnaireForm');
    const nextButton = document.getElementById('nextButton');
    const submitButton = document.getElementById('submitButton');
    const inputs = form.querySelectorAll('input[name="answer"]');

    function checkAnswerSelected() {
        let answerSelected = false;
        inputs.forEach(input => {
            if (input.checked) {
                answerSelected = true;
            }
        });

        // Show or hide the submit button based on the selection
        if (submitButton) {
            if (answerSelected) {
                submitButton.classList.remove('hidden');
                submitButton.disabled = false;
            } else {
                submitButton.classList.add('hidden');
                submitButton.disabled = true;
            }
        }

        // Show or hide the next button based on the selection
        if (nextButton) {
            if (answerSelected) {
                nextButton.classList.remove('hidden');
                nextButton.disabled = false;
            } else {
                nextButton.classList.add('hidden');
                nextButton.disabled = true;
            }
        }
    }

    // Attach event listeners
    inputs.forEach(input => {
        input.addEventListener('change', checkAnswerSelected);
    });

    // Initial check in case there are pre-selected answers (e.g., when navigating back)
    checkAnswerSelected();

    // Disable keyboard shortcuts for copy and paste
    document.addEventListener('keydown', function (e) {
        // Check if Ctrl key is pressed
        if (e.ctrlKey) {
            // Disable Ctrl+C (Copy)
            if (e.key === 'c' || e.key === 'C') {
                e.preventDefault();
            }
            // Disable Ctrl+V (Paste)
            if (e.key === 'v' || e.key === 'V') {
                e.preventDefault();
            }
        }
    }, false);
});
