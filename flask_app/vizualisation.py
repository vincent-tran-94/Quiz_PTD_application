import plotly
import plotly.graph_objs as go
from models import ReponseParticipant, db
import json
import pandas as pd

"""
Fonctions pour visualiser les graghes:
Les données des résultats seront affichés sur une page de visualisation qui contient  
Taux de réussite en moyenne calculé pour tout les participants à chaque catégorie 
Le nombre de participants répondus par catégorie  
Le nombre de participants répondus en fonction du mois pour chaque catégorie  
Le classement des 10 meilleurs participants (pour chaque mois et année) ayant répondu tout les catégories  
"""

def text_all_white_figure(fig):
    # Mettre tous les textes en blanc
    fig.update_layout(
        font=dict(
            color="white"  # Définir la couleur du texte en blanc
    )
)

colors = {'droit': 'rgb(31, 119, 180)', 
              'humanitaire': 'rgb(44, 160, 44)', 
              'vulgarisation': 'rgb(23, 190, 207)',
              'sociologie': 'rgb(255,127,80)'}

def get_participants_by_month():
    # Récupérer les données de la base de données (vérifier que les années 2024 à 2026 sont incluses)
    participants_data = db.session.query(ReponseParticipant.date_creation).all()

    # Créer un DataFrame Pandas à partir des données
    df = pd.DataFrame(participants_data, columns=['date_creation'])

    # Extraire l'année et le mois à partir de la colonne 'date_creation'
    df['year'] = df['date_creation'].dt.year
    df['month'] = df['date_creation'].dt.month

    # Filtrer les données pour les années de 2024 à 2026
    df = df[df['year'].isin([2024, 2025, 2026])]

    # Créer un dictionnaire pour stocker les données par année
    participants_by_year = {}
    
    # Compter le nombre de participants pour chaque mois pour chaque année
    for year in [2024, 2025, 2026]:
        monthly_counts = df[df['year'] == year]['month'].value_counts().sort_index()
        # Remplir avec 0 pour les mois sans participants
        monthly_counts = monthly_counts.reindex(range(1, 13), fill_value=0)
        participants_by_year[year] = monthly_counts

    # Traduire les mois en français
    french_months = {
        1: 'Janvier',
        2: 'Février',
        3: 'Mars',
        4: 'Avril',
        5: 'Mai',
        6: 'Juin',
        7: 'Juillet',
        8: 'Août',
        9: 'Septembre',
        10: 'Octobre',
        11: 'Novembre',
        12: 'Décembre'
    }

    # Créer les différentes traces pour chaque année dans le graphique
    traces = []
    colors = {'2024': 'skyblue', '2025': 'salmon', '2026': 'lightgreen'}
    for year, counts in participants_by_year.items():
        trace = go.Bar(
            x=[french_months[month] for month in counts.index],
            y=counts.values,
            name=f'Année {year}',
            marker=dict(color=colors[str(year)])
        )
        traces.append(trace)

    # Layout du graphique
    layout = go.Layout(
        title="Évolution mensuelle (2024-2026) du nombre de participants par catégorie aux questionnaires",
        xaxis=dict(title="Mois"),
        yaxis=dict(title="Nombre de participants", dtick=10),
        width=1070,
        height=400,
        paper_bgcolor='rgb(40, 55, 71)',
        plot_bgcolor='rgb(40, 55, 71)',  # Couleur de fond de la figure
        yaxis_gridcolor='white',  # Couleur de la grille sur l'axe des y
        barmode='group'  # Pour afficher les barres groupées par mois
    )

    fig = go.Figure(data=traces, layout=layout)
    text_all_white_figure(fig)

    # Convertir le graphique en JSON
    graph_json_participants_month = fig.to_json()

    return graph_json_participants_month


# Graphique pour le nombre de participants du taux de réussite par catégorie(diagramme en baton)
def get_participants_success_percentage():
    # Graphique pour le taux de réussite par catégorie
    categories = []
    success_percentages = []

    # Récupérer les données de succès pour chaque catégorie
    categories_data = db.session.query(ReponseParticipant.categorie, db.func.avg(ReponseParticipant.success_percentage))\
                                 .group_by(ReponseParticipant.categorie).all()

    for _, (category, success_percentage) in enumerate(categories_data):
        categories.append(category)
        success_percentages.append(success_percentage)


    pie_chart_success = go.Pie(
        labels=categories,
        values=success_percentages,
        marker=dict(colors=[colors[cat.lower()] for cat in categories], line=dict(color='black', width=1)),
        textinfo='percent',
        hole=0.3,
        
    )

    layout_success = go.Layout(
        title="Taux de réussite en moyenne par catégorie pour tous les participants",
        font=dict(size=11),
        width=575,  
        height=400,  
        paper_bgcolor='rgb(40, 55, 71)',
    )

    fig_success = go.Figure(data=[pie_chart_success], layout=layout_success)
    text_all_white_figure(fig_success)
    graph_json_success = json.dumps(fig_success, cls=plotly.utils.PlotlyJSONEncoder)

    return graph_json_success


# Graphique pour le nombre de participants par catégorie (diagramme circulaire)
def get_participants_count_by_category():
    categories = []
    participants_counts = []

    # Récupérer le nombre de participants pour chaque catégorie
    categories_data = db.session.query(ReponseParticipant.categorie, db.func.count(ReponseParticipant.participant_id))\
                                 .group_by(ReponseParticipant.categorie).all()

    for _, (category, count) in enumerate(categories_data):
        categories.append(category)
        participants_counts.append(count)


    pie_chart_participants = go.Pie(
        labels=categories,
        values=participants_counts,
        hole=0.3,
        marker=dict(colors=[colors[cat.lower()] for cat in categories],line=dict(color='black', width=1))
    )

    layout_participants = go.Layout(
        title="Nombre de participants répondus par catégorie",
        width=500,  # Largeur en pixels
        height=400,  # Hauteur en pixels
        paper_bgcolor='rgb(40, 55, 71)',
    )

    fig_participants = go.Figure(data=[pie_chart_participants], layout=layout_participants)
    text_all_white_figure(fig_participants )

    graph_json_participants = json.dumps(fig_participants, cls=plotly.utils.PlotlyJSONEncoder)

    return graph_json_participants


