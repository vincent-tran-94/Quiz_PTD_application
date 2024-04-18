function filterCurrentMonthYear() {

    var currentDate = new Date();
        
    var currentMonth = currentDate.getMonth() + 1; // Ajouter 1 car les mois sont 0-indexés

    var currentYear = currentDate.getFullYear();

    // Sélectionner le mois et l'année actuels dans la liste déroulante
    document.getElementById("month").value = currentMonth;
    document.getElementById("year").value = currentYear;
}
window.onload = filterCurrentMonthYear;
