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