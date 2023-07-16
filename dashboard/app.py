# import sys
import streamlit as st
from PIL import Image
import urllib.request
import pandas as pd
import seaborn as sns
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

# st.write(sys.executable)


# Config
st.set_page_config(
    page_title="🔍 Getaround Analysis",
    page_icon="🚗",
    layout="wide"
)
# App
st.title('📊 Getaround Dashboard')
# Loading Image and Text
urllib.request.urlretrieve(
    'https://lever-client-logos.s3.amazonaws.com/2bd4cdf9-37f2-497f-9096-c2793296a75f-1568844229943.png',
    "getaround_logo.png")
image = Image.open('getaround_logo.png')
col1, col2, col3 = st.columns([1.5, 5, 1.5])
# col2.image(image, caption='Getaround user in action (Credit: Getaround.com)')
st.markdown("""            
    Objectif de ce tableau de bord : \n\n
    En utilisant Getaround, les conducteurs réservent des voitures pour une période de temps spécifique : de quelques heures à quelques jours.\n
    Les utilisateurs doivent rendre la voiture à temps et il arrive de temps en temps que les conducteurs soient en retard au moment du checkout.\n
    Les retours tardifs peuvent générer des problèmes pour le conducteur suivant. \n
    Les retours tardifs peuvent entraîner des problèmes pour le conducteur suivant, urtout si la voiture est réservée le même jour, il en résulte des réactions négatives de la part des clients qui doivent attendre le retour de la voiture, et certains ont même annulé leur location. \n\n
    L'objectif de ce tableau de bord est de donner quelques indications sur l'impact de l'introduction d'un seuil de temps entre les locations. \n
    S'il y'a un seuil de temps, une voiture ne sera pas affichée dans les résultats de recherche si les heures d'enregistrement ou de départ demandées sont très proches.\n\n
    Allez Gooo, c'est parti!!!!
""")
st.markdown("---")


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_excel(fname, engine='openpyxl', sheet_name='rentals_data')
    return df


st.text('Chargement de données...')

fname = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx"

delay_df = pd.read_excel(fname, engine='openpyxl', sheet_name='rentals_data')

fname = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv"
pricing_df = pd.read_csv(fname, index_col=0)

color_discrete_sequence = ["#008000", "#ffbaba",
                           "#ff7b7b", "#ff5252", "#ff0000", "#a70000", "Black"]

# add checkout feature
delay_df['checkout'] = pd.cut(delay_df['delay_at_checkout_in_minutes'],
                              bins=[-np.inf, 0, 15, 30, 60, 120, np.inf],
                              labels=['Early', 'Late 0-15 mins', 'Late 15-30 mins', 'Late 30-60 mins', 'Late 1-2 hours', 'Late > 2 hours'],
                              right=False,
                              include_lowest=True)

fig0, ax0 = plt.subplots(figsize=(10,6))
sns.boxenplot(data=delay_df[delay_df['checkout']!='Early'], x='delay_at_checkout_in_minutes',scale='linear', ax=ax0)
st.pyplot(fig0)

st.subheader('Vue sur le Dataset')

if st.checkbox('Montrer les données traitées'):
    st.subheader('Affichage de 15 lignes aléatoires')
    st.write(delay_df.sample(15))
st.markdown(
    """
        Ce n'est pas le dataset original, il a été modifié.
    """
)
st.markdown("---")


category_orders = {"checkout": ["Early", "Late 0-15 mins", "Late 15-30 mins",
                                "Late 30-60 mins", "Late 1-2 hours", "Late > 2 hours", "NA"]}


st.header("Répartition des locations à l'heure ou en retard selon leur statut")
fig1 = px.histogram(delay_df.sort_values(by="delay_at_checkout_in_minutes"),
                    x='state',
                    color="checkout",
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig1, use_container_width=True)
st.markdown(
    """
        Environ 3 200 utilisateurs de Getaround ont annulé leur course, peut-être à cause du retard au moment du checkout.
    """
)
st.markdown("---")

st.header("Quel type de checkin est le plus concerné par les retards ?")
fig2 = px.histogram(delay_df.sort_values(by="delay_at_checkout_in_minutes"),
                    x='state',
                    facet_col='checkin_type',
                    color="checkout",
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

fig3 = px.histogram(delay_df.sort_values(by="delay_at_checkout_in_minutes"),
                    x="checkout",
                    color="checkout",
                    facet_row="checkin_type",
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig3, use_container_width=True)

connect_share = (delay_df['checkin_type'].value_counts()/delay_df['checkin_type'].count()*100)[1]
mobile_share = (delay_df['checkin_type'].value_counts()/delay_df['checkin_type'].count()*100)[0]
connect_canceled = (delay_df[delay_df['state']=='canceled']['checkin_type'].value_counts()/delay_df[delay_df['state']=='canceled']['checkin_type'].count()*100)[1]


st.write(f"Le checking par Mobile est plus utilisé avec {round(mobile_share,2)}% de pourcentage alors le checking par Connect a {round(connect_share,2)}% de pourcentage d'utilisation. \n On note que {round(connect_canceled)}% des annulations concernent Connect, ce qui suggère un impact plus important des annulations sur ce type ce type de location.")
st.markdown("---")

# Treshold
delay_df.dropna(subset=['delay_at_checkout_in_minutes'], inplace=True)
min = delay_df["delay_at_checkout_in_minutes"] <= delay_df["delay_at_checkout_in_minutes"].quantile(
    0.01)
max = delay_df["delay_at_checkout_in_minutes"] >= delay_df["delay_at_checkout_in_minutes"].quantile(
    0.99)
delay_df_bis = delay_df.loc[~ (min | max), :]

# late_drivers = delay_df_bis["delay_at_checkout_in_minutes"] > 0
overdue_df = delay_df[delay_df['delay_at_checkout_in_minutes']>0]
drivers_overdue = len(overdue_df)
drivers_total = len(delay_df)
percentage_drivers_late = drivers_overdue/drivers_total*100



st.header('Que peut on dire du seuil ?')

fig4 = px.histogram(overdue_df, x="delay_at_checkout_in_minutes",
                    histfunc='count', facet_row="checkin_type")
st.plotly_chart(fig4, use_container_width=True)

st.write(f"En moyenne, {round(percentage_drivers_late,2)} % des réservations sont en retard, soit {drivers_overdue} réservations sur {drivers_total}.")

time_overdue = overdue_df['delay_at_checkout_in_minutes'].sum()/len(overdue_df)
st.write(f"La moyenne de retard sur les réservations est de {round(time_overdue,2)} minutes.")

st.markdown("---")

st.header("Quelles sont les pertes entrainées par ces retards ? ?")

overdue_df_connect = overdue_df[overdue_df["checkin_type"] == "connect"]
overdue_df_mobile = overdue_df[overdue_df["checkin_type"] == "mobile"]
overdue_median_connect = np.median(overdue_df_connect["delay_at_checkout_in_minutes"])
overdue_median_mobile = np.median(overdue_df_mobile["delay_at_checkout_in_minutes"])

## Réservations annulées
st.subheader("Réservations annulées")
canceled = (delay_df['state'] == 'canceled').sum()
median_rental = pricing_df['rental_price_per_day'].median()
canceled_loss = canceled*median_rental 

st.write(f"En supposant une moyenne de location de 24 heures et en prenant une durée moyenne de location de 24h, les {canceled} annulations ont engrangé {canceled_loss} USD  de perte.")
st.write("En supposant bien sûr que ces annulations sont exclusivement liées aux rétards de précedentes réservations.")

## Connect Checkin Type
st.subheader("Checkin Connect")
# nb_delays = len(df_late_drivers_Connect)
nb_overdues = len(overdue_df_connect)
st.write(f"{nb_overdues} réservations sont impactées par les retards avec le mode connect.")
delay_median_connect = np.median(overdue_df_connect["delay_at_checkout_in_minutes"])
st.write(f"Le retard est d'environ : {overdue_median_connect} minutes.")
med_price_rent_by_day = np.median(pricing_df["rental_price_per_day"])  # price by day
avg_price_rent_by_min = med_price_rent_by_day / 1440
st.write(f"Sachant que la prix moyen de location d'une voiture est d'environ : {med_price_rent_by_day}USD/jour, on tourne autour de : {round(avg_price_rent_by_min, 3)}USD/min.")
lost_cash = avg_price_rent_by_min * overdue_median_connect
st.write(f"L'entreprise perdrait donc environ {round(lost_cash, 3)}USD/retard, ce qui répresente {round((lost_cash * nb_overdues), 2)}USD pour les {nb_overdues} retards.")
st.markdown("---")

# Mobile Checkin Type
st.subheader("Checkin Mobile")
# nb_delays = len(df_late_drivers_mobile)
nb_overdues = len(overdue_df_mobile)
st.write(f"{nb_overdues} réservations sont impactées par les retards avec le mode Mobile.")
delay_median_mobile = np.median(overdue_df_mobile["delay_at_checkout_in_minutes"])
st.write(f"Le retard est d'environ : {overdue_median_mobile} minutes.")
med_price_rent_by_day = np.median(pricing_df["rental_price_per_day"])  # price by day
avg_price_rent_by_min = med_price_rent_by_day / 1440
st.write(f"Sachant que la prix moyen de location d'une voiture est d'environ : {med_price_rent_by_day}USD/jour, on tourne autour de : {round(avg_price_rent_by_min, 3)}USD/min.")
lost_cash = avg_price_rent_by_min * overdue_median_mobile
st.write(f"L'entreprise perdrait donc environ {round(lost_cash, 3)}USD/retard, ce qui répresente {round((lost_cash * nb_overdues), 2)}USD pour les {nb_overdues} retards.")
st.markdown("---")
