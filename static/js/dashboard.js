function searchTable() {
    // Récupérer la valeur saisie dans l'input de recherche
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("filteredTableBody");
    tr = table.getElementsByTagName("tr");

    // Parcourir toutes les lignes de la table et masquer celles qui ne correspondent pas à la recherche
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[1]; // L'index 1 correspond à la colonne "Participant"
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

// Obtenir la date actuelle
var currentDate = new Date();
// Sélectionner le mois actuel
document.getElementById('month').value = currentDate.getMonth() + 1;
// Sélectionner l'année actuelle
document.getElementById('year').value = currentDate.getFullYear();


function saveFilters() {
    var selectedMonth = document.getElementById('month').value;
    var selectedYear = document.getElementById('year').value;
    localStorage.setItem('selectedMonth', selectedMonth);
    localStorage.setItem('selectedYear', selectedYear);
}

// Ajouter un gestionnaire d'événements pour le bouton "Filtrer"
document.getElementById('participantsTable').addEventListener('click', saveFilters);

// Obtenir les valeurs sélectionnées précédemment et les restaurer
var selectedMonth = localStorage.getItem('selectedMonth');
var selectedYear = localStorage.getItem('selectedYear');
if (selectedMonth && selectedYear) {
    document.getElementById('month').value = selectedMonth;
    document.getElementById('year').value = selectedYear;
}