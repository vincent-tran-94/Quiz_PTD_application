// Fonction de filtrage par nom
function searchTable() {
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

// Sauvegarder les filtres de mois et année dans le localStorage
function saveFilters() {
    var selectedMonth = document.getElementById('month').value;
    var selectedYear = document.getElementById('year').value;
    localStorage.setItem('selectedMonth', selectedMonth);
    localStorage.setItem('selectedYear', selectedYear);
}

// Charger les filtres de mois et année précédemment sélectionnés depuis le localStorage
var selectedMonth = localStorage.getItem('selectedMonth');
var selectedYear = localStorage.getItem('selectedYear');
if (selectedMonth && selectedYear) {
    document.getElementById('month').value = selectedMonth;
    document.getElementById('year').value = selectedYear;
}

// Attacher la sauvegarde des filtres de mois et année au bouton "Filtrer par Mois/Année"
document.getElementById('participantsTable').addEventListener('click', function() {
    saveFilters();
});
