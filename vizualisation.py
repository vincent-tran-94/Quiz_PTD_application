import plotly
import plotly.graph_objs as go
from models import ReponseParticipant, db
import json
import pandas as pd

def text_all_white_figure(fig):
    # Mettre tous les textes en blanc
    fig.update_layout(
        font=dict(
            color="white"  # Définir la couleur du texte en blanc
    )
)


def get_participants_by_month():
    # Récupérer les données de la base de données
    participants_data = db.session.query(ReponseParticipant.date_creation).all()

    # Créer un DataFrame Pandas à partir des données
    df = pd.DataFrame(participants_data, columns=['date_creation'])

    # Extraire le mois à partir de la colonne 'date_creation'
    df['month'] = df['date_creation'].dt.month

    # Compter le nombre de participants pour chaque mois
    participants_by_month = df['month'].value_counts().sort_index()

    #Remplir tout les participants à 0 pour le reste du mois en utilisant la méthode reindex.
    participants_by_month = participants_by_month.reindex(range(1, 13), fill_value=0) 

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
    
    #Mapper les valeurs de l'index de la série participants_by_month aux noms des mois en français.
    participants_by_month.index = participants_by_month.index.map(french_months)

    # Créer le graphique à barres
    bar_chart = go.Bar(
        x=participants_by_month.index,
        y=participants_by_month.values,
        marker=dict(color=['skyblue', 'salmon', 'lightgreen', 'orange', 'lightblue', 'yellow', 
                           'pink', 'cyan', 'purple', 'lime', 'brown', 'grey']),
    )

    layout = go.Layout(
        title="Évolution mensuelle en 2024 le nombre de participants ayant répondu aux questionnaires",
        xaxis=dict(title="Mois"),
        yaxis=dict(title="Nombre de participants",dtick=1),
        width=1070,  # Largeur en pixels
        height=400,  # Hauteur en pixels
        paper_bgcolor='rgb(40, 55, 71)',
        plot_bgcolor='rgb(40, 55, 71)',  # Couleur de fond de la figure
        yaxis_gridcolor='white',  # Couleur de la grille sur l'axe des y
    )

    fig = go.Figure(data=[bar_chart], layout=layout)
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

    colors = {'droit': 'rgb(31, 119, 180)', 
              'humanitaire': 'rgb(44, 160, 44)', 
              'culturel': 'rgb(23, 190, 207)'}

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
        width=575,  # Largeur en pixels
        height=400,  # Hauteur en pixels
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
        marker=dict(line=dict(color='black', width=1))
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