import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================
# CONFIGURATION DE LA PAGE
# ============================
st.set_page_config(
    page_title="Dashboard RATP - Fontaines & CV",
    page_icon="💧",
    layout="wide"
)

# ============================
# FONCTIONS DE PRÉPARATION DES DONNÉES
# ============================

@st.cache_data
def load_and_prepare_data():
    """
    Charge et prépare les données des fontaines à eau RATP.
    - Renomme les colonnes pour plus de clarté
    - Gère les valeurs manquantes
    - Crée des variables dérivées
    """
    # Chargement des données
    df = pd.read_csv('fontaines-a-eau-dans-le-reseau-ratp.csv', sep=';', encoding='utf-8-sig')
    
    # Renommage des colonnes pour plus de clarté
    df.columns = [
        'id_ratp', 'ligne', 'station', 'longitude', 'latitude', 
        'id_idm', 'adresse', 'code_postal', 'commune', 
        'num_acces', 'nom_acces', 'zone_controlee', 'point_geo'
    ]
    
    # Gestion des valeurs manquantes
    df['zone_controlee'] = df['zone_controlee'].fillna('non renseigné')
    df['nom_acces'] = df['nom_acces'].fillna('Non spécifié')
    
    # Création de variables dérivées
    df['type_ligne'] = df['ligne'].apply(lambda x: 'RER' if x in ['A', 'B', 'C', 'D', 'E'] else 'Métro')
    df['region'] = df['code_postal'].apply(lambda x: 'Paris' if x >= 75000 and x < 76000 else 'Banlieue')
    
    # Tri par ligne
    df = df.sort_values('ligne')
    
    return df

def create_line_distribution_chart(df):
    """Crée un graphique de distribution des fontaines par ligne"""
    line_counts = df['ligne'].value_counts().sort_index()
    
    fig = px.bar(
        x=line_counts.index,
        y=line_counts.values,
        labels={'x': 'Ligne', 'y': 'Nombre de fontaines'},
        title='Distribution des fontaines par ligne de métro/RER',
        color=line_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_title="Ligne",
        yaxis_title="Nombre de fontaines",
        font=dict(size=12),
        showlegend=False,
        height=400
    )
    
    return fig

def create_map_visualization(df_filtered):
    """Crée une carte interactive des fontaines avec couleurs officielles RATP"""
    
    # Dictionnaire des couleurs officielles RATP
    couleurs_ratp = {
        '1': '#FFCD00',   # Jaune
        '2': '#0064B0',   # Bleu
        '3': '#9F9825',   # Vert olive
        '4': '#C04191',   # Violet/Rose
        '5': '#F28E42',   # Orange
        '6': '#83C491',   # Vert clair
        '7': '#F3A4BA',   # Rose
        '8': '#CEADD2',   # Mauve
        '9': '#D5C900',   # Jaune
        '10': '#E3B32A',  # Jaune orangé
        '11': '#8D5E2A',  # Marron
        '12': '#00814F',  # Vert foncé
        '13': '#82C8E6',  # Bleu clair
        '14': '#8B5EA8',  # Violet
        'A': '#E3051C',   # Rouge
    
    }
    
    # Trier df_filtered par ligne pour l'ordre de la légende
    df_sorted = df_filtered.copy()
    
    # Fonction de tri personnalisée (chiffres puis lettres)
    def sort_key(ligne):
        ligne = str(ligne)
        if ligne.isdigit():
            return (0, int(ligne))
        elif ligne[:-3].isdigit() and ligne.endswith('bis'):
            return (0, int(ligne[:-3]) + 0.5)
        else:
            return (1, ligne)
    
    df_sorted['sort_key'] = df_sorted['ligne'].apply(sort_key)
    df_sorted = df_sorted.sort_values('sort_key')
    
    # Créer la carte
    fig = px.scatter_mapbox(
        df_sorted,
        lat='latitude',
        lon='longitude',
        hover_name='station',
        hover_data={'ligne': True, 'adresse': True, 'zone_controlee': True, 
                    'latitude': False, 'longitude': False, 'sort_key': False},
        color='ligne',
        color_discrete_map=couleurs_ratp,
        category_orders={'ligne': sorted(df_sorted['ligne'].unique(), key=sort_key)},
        zoom=11,
        title='Localisation géographique des fontaines'
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin={"r":0,"t":40,"l":0,"b":0},
        legend=dict(
            title="Ligne",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    fig.update_traces(marker=dict(size=14))
    
    return fig



def create_zone_comparison_chart(df):
    """Crée un graphique comparant zones contrôlées vs non contrôlées"""
    zone_counts = df['zone_controlee'].value_counts()
    
    fig = px.pie(
        values=zone_counts.values,
        names=zone_counts.index,
        title='Répartition des fontaines par type de zone',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def create_type_comparison_chart(df):
    """Compare Métro vs RER"""
    type_counts = df['type_ligne'].value_counts()
    
    fig = go.Figure(data=[
        go.Bar(
            x=type_counts.index,
            y=type_counts.values,
            text=type_counts.values,
            textposition='auto',
            marker_color=['#1f77b4', '#ff7f0e']
        )
    ])
    
    fig.update_layout(
        title='Comparaison Métro vs RER',
        xaxis_title='Type de transport',
        yaxis_title='Nombre de fontaines',
        height=400
    )
    
    return fig

# ============================
# CHARGEMENT DES DONNÉES
# ============================
df = load_and_prepare_data()

# ============================
# CRÉATION DES ONGLETS
# ============================
tab1, tab2, tab3 = st.tabs(["👤 CV Ismaël Gahlouzi", "📊 Dashboard Fontaines RATP", "📈 Analyses Détaillées"])

# ============================
# ONGLET 1 : DASHBOARD PRINCIPAL
# ============================
with tab2:
    st.title("💧 Dashboard d'analyse des fontaines à eau RATP")
    st.markdown("""
    Ce dashboard présente l'analyse des **81 fontaines à eau** installées dans le réseau RATP (métro et RER).
    Explorez la distribution, la localisation et les caractéristiques de ces équipements.
    """)
    
    st.markdown("---")
    
    # KPIs en haut
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total fontaines", len(df))
    
    with col2:
        st.metric("Lignes équipées", df['ligne'].nunique())
    
    with col3:
        st.metric("Communes desservies", df['commune'].nunique())
    
    with col4:
        zone_ctrl = len(df[df['zone_controlee'] == 'en zone contrôlée'])
        st.metric("En zone contrôlée", zone_ctrl)
    
    st.markdown("---")
    
    # Filtres interactifs
    st.subheader("🔍 Filtres interactifs")
    
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        selected_lines = st.multiselect(
            "Sélectionner les lignes",
            options=sorted(df['ligne'].unique()),
            default=sorted(df['ligne'].unique())
        )
    
    with col_filter2:
        selected_type = st.selectbox(
            "Type de transport",
            options=['Tous', 'Métro', 'RER']
        )
    
    with col_filter3:
        selected_zone = st.selectbox(
            "Zone contrôlée",
            options=['Toutes', 'en zone contrôlée', 'non renseigné']
        )
    
    # Application des filtres
    df_filtered = df[df['ligne'].isin(selected_lines)]
    
    if selected_type != 'Tous':
        df_filtered = df_filtered[df_filtered['type_ligne'] == selected_type]
    
    if selected_zone != 'Toutes':
        df_filtered = df_filtered[df_filtered['zone_controlee'] == selected_zone]
    
    st.info(f"**{len(df_filtered)} fontaines** correspondent à vos critères de filtrage")
    
    st.markdown("---")
    
    # Visualisations principales
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.plotly_chart(create_line_distribution_chart(df_filtered), use_container_width=True)
    
    with col_viz2:
        st.plotly_chart(create_zone_comparison_chart(df_filtered), use_container_width=True)
    
    # Carte interactive
    st.subheader("🗺️ Carte interactive des fontaines")
    st.plotly_chart(create_map_visualization(df_filtered), use_container_width=True)
    
    # Tableau de données
    st.subheader("📋 Données filtrées")
    st.dataframe(
        df_filtered[['ligne', 'station', 'adresse', 'commune', 'zone_controlee']],
        use_container_width=True,
        height=300
    )

# ============================
# ONGLET 2 : ANALYSES DÉTAILLÉES
# ============================
with tab3:
    st.title("📈 Analyses détaillées")
    
    st.markdown("---")
    
    # Comparaison Métro vs RER
    col_analysis1, col_analysis2 = st.columns(2)
    
    with col_analysis1:
        st.plotly_chart(create_type_comparison_chart(df), use_container_width=True)
        st.info("ℹ️ **Note** : Dans ce jeu de données, seule la ligne **RER A** est représentée (6 fontaines). Les autres lignes RER (B, C, D, E) ne figurent pas dans les données disponibles.")

    
    with col_analysis2:
        st.subheader("Répartition Paris vs Banlieue")
        region_counts = df['region'].value_counts()
        
        fig = px.pie(
            values=region_counts.values,
            names=region_counts.index,
            title='Distribution géographique',
            color_discrete_sequence=['#636EFA', '#EF553B']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Top 10 des lignes
        # Top 10 des lignes
    st.subheader("🏆 Top 10 des lignes les mieux équipées")
    
    top_lines = df['ligne'].value_counts().head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            x=top_lines.values,
            y=top_lines.index.astype(str),
            orientation='h',
            text=top_lines.values,
            textposition='outside',
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        xaxis_title="Nombre de fontaines",
        yaxis_title="Ligne",
        height=400,
        yaxis={'categoryorder': 'total ascending'},
        xaxis=dict(range=[0, top_lines.values.max() * 1.15])  # Ajoute de l'espace pour les valeurs
    )
    
    st.plotly_chart(fig, use_container_width=True)

    
    st.markdown("---")
    
    # Analyse textuelle
    st.subheader("📝 Principaux enseignements")
    
    st.markdown(f"""
    ### Observations clés :
    
    1. **Couverture du réseau** : {len(df)} fontaines réparties sur {df['ligne'].nunique()} lignes différentes
    
    2. **Distribution inégale** : Les lignes **{', '.join(df['ligne'].value_counts().head(4).index.astype(str))}** 
       sont les mieux équipées avec respectivement 9 fontaines chacune.
    
    3. **Accessibilité** : Seulement **{len(df[df['zone_controlee'] == 'en zone contrôlée'])} fontaines ({len(df[df['zone_controlee'] == 'en zone contrôlée'])/len(df)*100:.1f}%)** 
       sont situées en zone contrôlée (après validation du titre de transport)
    
    4. **Couverture géographique** : {len(df[df['region'] == 'Paris'])} fontaines à Paris et {len(df[df['region'] == 'Banlieue'])} en banlieue
    
    5. **Recommandations** : 
       - Augmenter le nombre de fontaines sur les lignes les moins équipées
       - Équilibrer la répartition entre Paris et banlieue
       - Améliorer l'accessibilité en installant plus de fontaines hors zones contrôlées
    """)

# ============================
# ONGLET 3 : CV
# ============================
with tab1:
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        st.markdown("### Ismaël Gahlouzi")
        st.markdown("**Data Analyst**")
        st.markdown("---")

        
        
        
        st.markdown("**📞 Contact :**")
        st.write("📍 95240 Cormeilles-En-Parisis")
        st.write("📱 06 21 08 79 91")
        st.write("📧 isgahlouzi@gmail.com")
        st.markdown("---")
        
        st.markdown("**🌍 Langues :**")
        st.write("Anglais : B2")
        st.write("Espagnol : B1")
        st.markdown("---")
        
        st.markdown("**💪 Soft Skills :**")
        st.write("✓ Rigoureux")
        st.write("✓ Sens de l'organisation")
        st.write("✓ Autonome")
        st.write("✓ Curiosité")
        st.write("✓ Travail en équipe")
        st.markdown("---")
        
        st.markdown("**🎯 Centres d'intérêt :**")
        st.write("⚽ Sports collectifs")
        st.write("🎬 Cinéma")
        st.write("🎮 Jeux vidéo")
        st.markdown("---")
        
        st.markdown("**🚗 Permis**")
        st.write("Permis B")
    
    with col_right:
        st.header("🎯 Objectif professionnel")
        st.write(
            "Attiré par le monde de la donnée et fasciné par son évolution, je souhaite, "
            "à l'aide de ma rigueur, mon sens de l'analyse et mes compétences, acquérir de "
            "nombreux savoir-faire au sein d'un organisme passionné par la data, l'intelligence "
            "artificielle ou le cloud."
        )
        
        st.header("💼 Expériences professionnelles")
        
        st.subheader("Alternance chez KPMG en tant que Data Analyst (2023 - Présent)")
        st.write("""
        - Analyse et traitement des données clients pour améliorer la prise de décision
        - Création de tableaux de bord interactifs avec Power BI pour le suivi des indicateurs clés
        - Automatisation de rapports mensuels via Python pour réduire le temps de production
        - Collaboration avec les équipes métiers pour comprendre leurs besoins et optimiser les outils de data visualisation
        """)
        
        st.subheader("Jobs étudiants - manutention (2023)")
        st.write("Expérience professionnelle orientée tâches opérationnelles et travail en équipe.")
        
        st.header("🎓 Formations")
        
        st.subheader("BUT Science des Données (3ème année) — IUT Paris Rives de Seine (2023-2026)")
        st.write("- Organisation, exploitation et synthèse de données")
        st.write("- Analyse statistique, data mining, indicateurs de performance")
        st.write("- Communication orale et écrite des résultats")
        
        st.subheader("Licence Sciences formelles — Sorbonne Université (2022-2023)")
        st.write("- Mathématiques fondamentales et appliquées")
        st.write("- Informatique théorique et programmation")
        st.write("- Statistiques et probabilités avancées")
        
        st.subheader("Baccalauréat Général — Lycée Julie Victoire Daubié (2019-2022)")
        st.write("- Spécialités : Physique Chimie, SVT, maths complémentaires")
        st.write("- Mention Bien")
        
        st.header("🚀 Projets")
        
        st.write("**📊 Dashboard RATP** : Application Streamlit d'analyse des fontaines à eau dans le réseau RATP (Plotly, Pandas)")
        st.write("**📋 Réalisation d'une enquête** : Création d'un sondage sur le thème de l'IA, analyse et présentation (Excel, PowerPoint)")
        st.write("**🦠 Étude de cas Covid-19** : Synthèse et création de graphiques pour explorer les répercussions psychologiques (Excel, Word)")
        st.write("**💰 Reporting magasin DVD** : Requêtes SQL pour recueillir des informations et améliorer le chiffre d'affaires")
        st.write("**📁 Lecture / écriture de fichiers** : Nettoyage et conversion d'un jeu de données texte en CSV à l'aide de Python")
        
        st.header("🛠️ Compétences")
        
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            st.subheader("✅ Maîtrisées")
            st.markdown("""
            - 🐍 **Python** (Pandas, Plotly, Streamlit)
            - 📊 **R** (statistiques, visualisation)
            - 🐬 **SQL** (requêtes, jointures)
            - 📊 **Excel** (tableaux croisés, graphiques)
            - 📄 **Word** (rapports professionnels)
            - 📈 **PowerPoint** (présentations)
            """)
        
        with col_comp2:
            st.subheader("🔄 En apprentissage")
            st.markdown("""
            - 📊 **Power BI** (dashboards)
            - 🗃️ **Access** (bases de données)
            - 📈 **SAS** (analyse statistique)
            - ⚙️ **VBA** (automatisation Excel)
            """)

# ============================
# FOOTER
# ============================
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        💧 Dashboard créé par Ismaël Gahlouzi | Données : Open Data RATP | 
        Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y')}
    </div>
    """, 
    unsafe_allow_html=True
)
