import streamlit as sl
import pandas as pd
import plotly.express as px

from streamlit_option_menu import option_menu
from numerize.numerize import numerize

sl.set_page_config(page_title ="Dashboard",page_icon= "🌍",layout="wide")
sl.subheader("🚗 Car resale price analysis and prediction")
sl.markdown("##")
df = pd.read_csv('data/car_resale_final_app.csv')
df = df.drop(['Unnamed: 0'], axis=1)
# sl.dataframe(df)

sl.sidebar.image("data/logo1.png",caption ="resale-predictor")

sl.sidebar.header("Please filter")
city = sl.sidebar.multiselect(
    "Select city",
    options = df.city.unique(),
    default=df.city.mode()
)
insurance_type = sl.sidebar.multiselect(
    "Select Insurance type",
    options = df.insurance.unique(),
    default=df.insurance.mode()
)

transmission_type = sl.sidebar.multiselect(
    "Select Transmission type",
    options = df.transmission_type.unique(),
    default=df.transmission_type.mode()
)

owner_type = sl.sidebar.multiselect(
    "Select owner type",
    options = df.owner_type.unique(),
    default=df.owner_type.mode()
)

fuel_type = sl.sidebar.multiselect(
    "Select fuel type",
    options = df.fuel_type.unique(),
    default=df.fuel_type.mode()
)

body_type = sl.sidebar.multiselect(
    "Select body type",
    options = df.body_type.unique(),
    default=df.body_type.mode()
)

model = sl.sidebar.multiselect(
    "Select vehcle model",
    options = df.model.unique(),
    default=df.model.mode()
)

df_s = df.query(
    '''city == @city \
        & insurance == @insurance_type \
        & owner_type == @owner_type \
        & transmission_type==@transmission_type \
        & fuel_type == @fuel_type \
        & body_type == @body_type \
        & model == @model
        ''')
# sl.dataframe(df_s)

def Home():
    with sl.expander("Tabular"):
        showData = sl.multiselect('Filter: ',df_s.columns,default=[])
        sl.write(df_s[showData])

        max_price = float(df_s.resale_price.max())
        mean_price = float(df_s.resale_price.mean())
        median_price = float(df_s.resale_price.median())
        avg_kms = float(df_s.kms_driven.mean())


Home()