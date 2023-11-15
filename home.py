import streamlit as sl
import pandas as pd
import plotly.express as px

from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import plotly.graph_objs as go

import time

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
    default=df.city.unique()
)
insurance_type = sl.sidebar.multiselect(
    "Select Insurance type",
    options = df.insurance.unique(),
    default=df.insurance.unique()
)

transmission_type = sl.sidebar.multiselect(
    "Select Transmission type",
    options = df.transmission_type.unique(),
    default=df.transmission_type.unique()
)

owner_type = sl.sidebar.multiselect(
    "Select owner type",
    options = df.owner_type.unique(),
    default=df.owner_type.unique()
)

fuel_type = sl.sidebar.multiselect(
    "Select fuel type",
    options = df.fuel_type.unique(),
    default=df.fuel_type.unique()
)

body_type = sl.sidebar.multiselect(
    "Select body type",
    options = df.body_type.unique(),
    default=df.body_type.unique()
)

model = sl.sidebar.multiselect(
    "Select vehcle model",
    options = df.model.unique(),
    default=df.model.unique()
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
        average_prices = df_s.groupby('model')['resale_price'].mean()
        sorted_models = average_prices.sort_values(ascending=False)
        models = sorted_models.head(1)
        most_preferred_model = models.index[0]

        a,b,c,d,e =sl.columns(5,gap='large')
        with a:
            sl.info('Maximum sale price',icon='🤑')
            sl.metric(label = 'max price', value=f'Rs {numerize(max_price)}',label_visibility="hidden")
        with b:
            sl.info('Average sale price',icon='💸')
            sl.metric(label = 'avg price', value=f'Rs {numerize(mean_price)}',label_visibility="hidden")
        
        with c:
            sl.info('Median sale price',icon='💶')
            sl.metric(label = 'median price', value=f'Rs {numerize(median_price)}',label_visibility="hidden")
        with d:
            sl.info('Average distance driven',icon='🛣️')
            sl.metric(label = 'avg dist', value=f' {numerize(avg_kms)}',label_visibility="hidden")
        with e:
            sl.info('Most prefered model',icon='🌟')
            sl.subheader(str(most_preferred_model))

def graphs():
    price_by_insurance = (
        df_s.groupby(by=['insurance']).count()[['resale_price']].sort_values(by='resale_price')
    )
    fig_insurance = px.bar(
        price_by_insurance,
        x = 'resale_price',
        y=price_by_insurance.index,
        orientation='h',
        title='<b>Insurance by Resale price </b>',
        color_discrete_sequence=['#0083b8']*len(price_by_insurance),
        template='plotly_white',
    )

    fig_insurance.update_layout(
        plot_bgcolor="rgb(0,0,0,0)",
        xaxis = (dict(showgrid=False))
    )

    price_by_city = (
        df_s.groupby(by=['city']).count()[['resale_price']]
    )
    fig_city = px.line(
        price_by_city,
        x = price_by_city.index,
        y='resale_price',
        orientation='h',
        title='<b>Sale price by city</b>',
        color_discrete_sequence=['#0083b8']*len(price_by_city),
        template='plotly_white',
    )
    fig_city.update_layout(
        xaxis = (dict(tickmode='linear')),
        plot_bgcolor="rgb(0,0,0,0)",
        yaxis = (dict(showgrid=False))
    )

    left,right = sl.columns(2)
    left.plotly_chart(fig_city,use_container_width = True)
    right.plotly_chart(fig_insurance,use_container_width = True)

def Progressbar():
    sl.markdown("""<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""",unsafe_allow_html=True,)
    target=df.resale_price.max()
    current=df_s["resale_price"].mean()
    percent=round((current/target*100))
    mybar=sl.progress(0)

    if percent>100:
        sl.subheader("Target done !")
    else:
     sl.write("filtered resale price is ",percent, "% " ,"of ",'Rs. ', target)
     for percent_complete in range(percent):
        time.sleep(0.1)
        mybar.progress(percent_complete+1,text=" Target Percentage")

def sideBar():
 with sl.sidebar:
    selected=option_menu(
        menu_title="Main Menu",
        options=["Home","Progress"],
        icons=["house","eye"],
        menu_icon="cast",
        default_index=0,
    )
 if selected=="Home":
    Home()
    graphs()
 if selected=="Progress":
    Progressbar()
    graphs()

sideBar()
sl.sidebar.image("data/logo1.png",caption="")

sl.subheader('PICK FEATURES TO EXPLORE DISTRIBUTIONS TRENDS BY QUARTILES',)
feature_y = sl.selectbox('Select feature for y Quantitative Data', df_s.select_dtypes("number").columns)
fig2 = go.Figure(
    data=[go.Box(x=df['insurance'], y=df[feature_y])],
    layout=go.Layout(
        title=go.layout.Title(text="INSURANCE TYPE BY QUARTILES OF RESALE PRICE"),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        font=dict(color='#cecdcd'),
    )
)

sl.plotly_chart(fig2,use_container_width=True)

#theme
hide_st_style=""" 

<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
