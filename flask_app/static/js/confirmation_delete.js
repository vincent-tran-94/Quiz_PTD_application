let isDeleting = false; // Indicateur de suppression

function showConfirmation(categorie, sujet, button) {
    isDeleting = true; // Activation de l'indicateur de suppression
    button.style.display = 'none';
    const confirmationDiv = button.nextElementSibling;
    confirmationDiv.style.display = 'block';
}

function hideConfirmation(cancelButton) {
    isDeleting = false; // Désactivation de l'indicateur de suppression
    const confirmationDiv = cancelButton.parentElement;
    confirmationDiv.style.display = 'none';
    const deleteButton = confirmationDiv.previousElementSibling;
    deleteButton.style.display = 'inline-block';
}

document.querySelector('.btn-secondary').addEventListener('click', function(e) {
    if (isDeleting) {
        e.preventDefault(); // Empêche le redirection si une suppression est en cours
        alert("Veuillez confirmer ou annuler la suppression avant de naviguer ailleurs.");
    }

});