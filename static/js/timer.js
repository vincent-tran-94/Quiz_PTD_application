document.addEventListener('copy', function(e) {
    // Annuler l'action de copie par défaut
    e.preventDefault();
    // Afficher un message ou effectuer une autre action
});

var timer = 600; // 12 minutes
var warnings = 0;
let ButtonClicked = false;

function reduceTime() {
    timer -= 30;
    var minutes = Math.floor(timer / 60);
    var seconds = timer % 60;
    document.getElementById('countdown').innerHTML = 'Temps restant : ' + minutes + 'm ' + seconds + 's';
    if (timer <= 0) {
        clearInterval(countdown);
        alert('Le temps est écoulé. Vous allez être redirigé vers la page d\'accueil.');
        window.location.href = "{{ url_for('accueil') }}"; // Redirection vers la page d'accueil
        document.forms["questionnaireForm"].submit(); // Soumettre le formulaire lorsque le temps est écoulé
    }
}

function handleWarnings() {
    if (!ButtonClicked) {
        if (warnings == 1) {
            alert("Attention : Quitter cette page réduira le temps restant.");
        } else if (warnings >= 2) {
            alert("Attention : Vous avez perdu 30 secondes.");
            reduceTime();
        }
    }
}

document.querySelector('.btn.btn-primary.mt-3').addEventListener('click', function() {
    ButtonClicked = true;
});

document.querySelector('#accueilBtn').addEventListener('click', function() {
    ButtonClicked = true;
});

document.addEventListener('visibilitychange', function () {
    if (!ButtonClicked) {
        handleWarnings();
        warnings++;
    }
});

document.addEventListener('DOMContentLoaded', function () {
    var countdown = setInterval(function () {
        timer--;
        var minutes = Math.floor(timer / 60);
        var seconds = timer % 60;
        document.getElementById('countdown').innerHTML = 'Temps restant : ' + minutes + 'm ' + seconds + 's';
        if (timer <= 0) {
            clearInterval(countdown);
            alert('Le temps est écoulé. Vous allez être redirigé vers la page d\'accueil.');
            window.location.href = "{{ url_for('accueil') }}"; // Redirection vers la page d'accueil
            document.forms["questionnaireForm"].submit(); // Soumettre le formulaire lorsque le temps est écoulé
        }
    }, 1000); // Mettre à jour toutes les secondes
});