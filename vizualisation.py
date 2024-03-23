import plotly
import plotly.graph_objs as go
from models import ReponseParticipant, db
import json

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

    bar_chart_success = go.Bar(
        x=categories,
        y=success_percentages,
        text=success_percentages,
        textposition='auto',
        marker=dict(color=[colors[cat.lower()] for cat in categories]),
        opacity=0.6
    )

    layout_success = go.Layout(
        title="Graphique illustrant la moyenne des taux de réussite par catégorie pour tous les participants.",
        xaxis=dict(title='Catégorie'),
        yaxis=dict(title='Pourcentage de succès'),
    )

    fig_success = go.Figure(data=[bar_chart_success], layout=layout_success)
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
        hole=0.3
    )

    layout_participants = go.Layout(
        title="Nombre de participants par catégorie",
    )

    fig_participants = go.Figure(data=[pie_chart_participants], layout=layout_participants)
    graph_json_participants = json.dumps(fig_participants, cls=plotly.utils.PlotlyJSONEncoder)

    return graph_json_participants