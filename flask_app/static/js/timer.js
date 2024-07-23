var timer = 600; // 1 minutes
var warnings = 0;
let ButtonClicked = false;
var isRedirected = false; // Ajout de la variable pour suivre si la redirection a eu lieu

function updateProgressBar() {
    var progressBar = document.getElementById('progressBar');
    var percentage = ((600 - timer) / 600) * 100;
    progressBar.style.width = percentage + '%';
}

function reduceTime() {
    timer -= 30;
    updateProgressBar();
    saveTimer();
    if (timer <= 0) {
        clearInterval(countdown);
        if (!isRedirected) {
        window.location.href = "{{ url_for('progression') }}"; // Redirection vers la page d'accueil
        document.forms["questionnaireForm"].submit(); // Soumettre le formulaire lorsque le temps est écoulé
        isRedirected = true; // Marquer que la redirection a eu lieu
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
    } else if (timer == 0) {
        timer = 600; // Initialiser à 600 secondes (10 minutes) si aucune valeur n'est trouvée
    }
}

function handleTimerEnd() {
    timer = 0; // Réinitialiser le timer à 0
    localStorage.removeItem('remainingTime'); // Supprimer l'entrée du stockage local
    if (!isRedirected) {
        alert('Le temps est écoulé. Vous allez être redirigé vers la page des résultats.');
        window.location.href = "{{ url_for('progression') }}"; // Redirection vers la page d'accueil
        document.forms["questionnaireForm"].submit(); // Soumettre le formulaire lorsque le temps est écoulé
        isRedirected = true; // Marquer que la redirection a eu lieu
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
    loadTimer(); // Charger le timer depuis le stockage local
    updateProgressBar();
    var countdown = setInterval(function () {
        timer--;
        updateProgressBar();
        saveTimer();
        if (timer <= 0) {
            clearInterval(countdown);
            handleTimerEnd();
        }
    }, 1000); // Mettre à jour toutes les secondes
});

