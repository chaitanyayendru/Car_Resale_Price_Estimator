import streamlit as sl
import pandas as pd
import plotly.express as px
from decimal import Decimal

from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import plotly.graph_objs as go
import pickle as pkl
import time
import base64

sl.set_page_config(page_title ="Dashboard",page_icon= "🌍",layout="wide")
sl.subheader("🚗 Car resale price analysis and prediction")
sl.markdown("##")
df = pd.read_csv('data/car_resale_final_app.csv')
df = df.drop(['Unnamed: 0'], axis=1)
# sl.dataframe(df)
sl.sidebar.image("data/RQ1.png",caption="")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    sl.markdown(page_bg_img, unsafe_allow_html=True)

def Add_Analytic_Filters():

    sl.sidebar.header("Please filter")
    city = sl.sidebar.multiselect(
        "Select city",
        options = df.city.unique(),
        default=df.city.unique()[:5]
    )
    insurance_type = sl.sidebar.multiselect(
        "Select Insurance type",
        options = df.insurance.unique(),
        default=df.insurance.mode()
    )

    transmission_type = sl.sidebar.multiselect(
        "Select Transmission type",
        options = df.transmission_type.unique(),
        default=df.transmission_type.unique()
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

    global df_s
    df_s = df.query(
        '''city == @city \
            & insurance == @insurance_type \
            & owner_type == @owner_type \
            & transmission_type==@transmission_type \
            & fuel_type == @fuel_type \
            & body_type == @body_type \
            & model == @model
            ''')

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


def Plot_QuantitaveData_Trends():
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

def Predict():

# Numeric inputs with validation
    user_kms_driven = sl.sidebar.number_input("Enter KMs Driven", min_value=0.0, value = df.kms_driven.mean())
    numerical_features = ['resale_price',
 'engine_capacity',
 'kms_driven',
 'max_power',
 'seats',
 'mileage',
 'model_year',
 'car_age']
    
    min_values = df[numerical_features].min()
    max_values = df[numerical_features].max()
    
    user_engine_capacity = sl.sidebar.number_input("Enter Engine Capacity", min_value=0.0, value = df.engine_capacity.mean())
    user_seats = sl.sidebar.number_input("Enter Seats in the vehicle", min_value=0, value = int(df.seats.mean()))
    user_model_year = sl.sidebar.number_input("Enter Model Year", min_value=0, value = int(df.model_year.mean()))
    user_mileage = sl.sidebar.number_input("Enter Mileage", min_value=0.0, value = df.mileage.mean())
    user_max_power = sl.sidebar.number_input("Enter Max Power", min_value=0.0, value = df.max_power.mean())
    user_car_age = sl.sidebar.number_input("Enter Car Age", min_value=0, value = 2023 - user_model_year)

    user_car_age = (user_car_age)/21
    user_kms_driven = (user_kms_driven - min_values['kms_driven'])/(max_values['kms_driven']-min_values['kms_driven'])
    user_engine_capacity = (user_engine_capacity - min_values['engine_capacity'])/(max_values['engine_capacity']-min_values['engine_capacity'])
    user_seats = (user_seats - min_values['seats'])/(max_values['seats']-min_values['seats'])
    user_model_year = (user_model_year - min_values['model_year'])/(max_values['model_year']-min_values['model_year'])
    user_mileage = (user_mileage - min_values['mileage'])/(max_values['mileage']-min_values['mileage'])
    user_max_power = (user_max_power - min_values['max_power'])/(max_values['max_power']-min_values['max_power'])
    
    categorical_features = [
 'insurance_Comprehensive',
 'insurance_Not Available',
 'insurance_Third Party',
 'insurance_Third Party insurance',
 'insurance_Zero Dep',
 'transmission_type_Automatic',
 'transmission_type_Manual',
 'owner_type_Fifth Owner',
 'owner_type_First Owner',
 'owner_type_Fourth Owner',
 'owner_type_Second Owner',
 'owner_type_Third Owner',
 'fuel_type_CNG',
 'fuel_type_Diesel',
 'fuel_type_LPG',
 'fuel_type_Petrol',
 'body_type_Hatchback',
 'body_type_MUV',
 'body_type_Minivans',
 'body_type_SUV',
 'body_type_Sedan',
 'city_Agra',
 'city_Ahmedabad',
 'city_Bangalore',
 'city_Chandigarh',
 'city_Chennai',
 'city_Delhi',
 'city_Gurgaon',
 'city_Hyderabad',
 'city_Jaipur',
 'city_Kolkata',
 'city_Lucknow',
 'city_Mumbai',
 'city_Pune',
 'model_BMW 1',
 'model_Chevrolet Aveo',
 'model_Chevrolet Beat',
 'model_Chevrolet Enjoy',
 'model_Chevrolet Optra',
 'model_Chevrolet Sail',
 'model_Chevrolet Spark',
 'model_Citroen C3',
 'model_Datsun GO',
 'model_Datsun RediGO',
 'model_Fiat Abarth',
 'model_Fiat Avventura',
 'model_Fiat Grande',
 'model_Fiat Linea',
 'model_Fiat Punto',
 'model_Ford Aspire',
 'model_Ford Ecosport',
 'model_Ford Fiesta',
 'model_Ford Figo',
 'model_Ford Freestyle',
 'model_Honda Amaze',
 'model_Honda BR-V',
 'model_Honda Brio',
 'model_Honda CR-V',
 'model_Honda City',
 'model_Honda Civic',
 'model_Honda Jazz',
 'model_Honda Mobilio',
 'model_Honda WR-V',
 'model_Hyundai Accent',
 'model_Hyundai Alcazar',
 'model_Hyundai Aura',
 'model_Hyundai Creta',
 'model_Hyundai EON',
 'model_Hyundai Elantra',
 'model_Hyundai Elite',
 'model_Hyundai Grand',
 'model_Hyundai Santro',
 'model_Hyundai Venue',
 'model_Hyundai Verna',
 'model_Hyundai Xcent',
 'model_Hyundai i10',
 'model_Hyundai i20',
 'model_Kia Carens',
 'model_Kia Seltos',
 'model_Kia Sonet',
 'model_MG Astor',
 'model_MG Hector',
 'model_Mahindra Bolero',
 'model_Mahindra KUV',
 'model_Mahindra Marazzo',
 'model_Mahindra NuvoSport',
 'model_Mahindra Quanto',
 'model_Mahindra Supro',
 'model_Mahindra TUV',
 'model_Mahindra Verito',
 'model_Mahindra XUV300',
 'model_Maruti 800',
 'model_Maruti A-Star',
 'model_Maruti Alto',
 'model_Maruti Baleno',
 'model_Maruti Brezza',
 'model_Maruti Celerio',
 'model_Maruti Ciaz',
 'model_Maruti Eeco',
 'model_Maruti Ertiga',
 'model_Maruti Grand',
 'model_Maruti Ignis',
 'model_Maruti Jimny',
 'model_Maruti Omni',
 'model_Maruti Ritz',
 'model_Maruti S-Presso',
 'model_Maruti SX4',
 'model_Maruti Swift',
 'model_Maruti Vitara',
 'model_Maruti Wagon',
 'model_Maruti XL6',
 'model_Maruti Zen',
 'model_Mercedes-Benz A',
 'model_Mercedes-Benz B',
 'model_Mini 5',
 'model_Mini Cooper',
 'model_Nissan Kicks',
 'model_Nissan Magnite',
 'model_Nissan Micra',
 'model_Nissan Sunny',
 'model_Nissan Terrano',
 'model_Renault Captur',
 'model_Renault Duster',
 'model_Renault Fluence',
 'model_Renault KWID',
 'model_Renault Kiger',
 'model_Renault Lodgy',
 'model_Renault Pulse',
 'model_Renault Scala',
 'model_Renault Triber',
 'model_Skoda Fabia',
 'model_Skoda Kushaq',
 'model_Skoda Octavia',
 'model_Skoda Rapid',
 'model_Skoda Slavia',
 'model_Tata Altroz',
 'model_Tata Bolt',
 'model_Tata Indica',
 'model_Tata Indigo',
 'model_Tata Manza',
 'model_Tata Nexon',
 'model_Tata Punch',
 'model_Tata Tiago',
 'model_Tata Tigor',
 'model_Tata Zest',
 'model_Toyota Corolla',
 'model_Toyota Etios',
 'model_Toyota Glanza',
 'model_Toyota Hyryder',
 'model_Toyota Urban',
 'model_Toyota Yaris',
 'model_Volkswagen Ameo',
 'model_Volkswagen CrossPolo',
 'model_Volkswagen Jetta',
 'model_Volkswagen Polo',
 'model_Volkswagen Taigun',
 'model_Volkswagen Vento',
 'model_Volkswagen Virtus']
    selected_insurance, selected_transmission, selected_owner, selected_fuel_type, selected_body,selected_city,selected_model = None,None,None,None,None,None,None
    selections = [selected_insurance, selected_transmission, selected_owner, selected_fuel_type, selected_body,selected_city,selected_model]
    category_labels = ['insurance', 'transmission_type','owner_type','fuel_type','body_type','city','model']
    for i, s in enumerate(selections):
        columns = [col for col in categorical_features if category_labels[i] in col]
        options = ['Unknown'] + list(set([col.split('_')[-1] for col in columns]))
        selections[i] = sl.sidebar.selectbox(f"Select {category_labels[i]} of the vehicle", options=options)

    for index, label in enumerate(category_labels):
        if selections[index] == 'Unknown':
            selections[index] = df[label].mode().iloc[0]  # Use iloc[0] to get the actual value

    selected_columns = [f'{label}_{selection}' for label, selection in zip(category_labels, selections)]
    numerical_data = {
        'engine_capacity': [user_engine_capacity],
        'kms_driven': [user_kms_driven],
        'max_power': [user_max_power],
        'seats': [user_seats],
        'mileage': [user_mileage],
        'model_year': [user_model_year],
        'car_age': [user_car_age],
    }

    categorical_data = {col: 1 if col in selected_columns else 0 for col in categorical_features}
    data_dict = {**numerical_data, **categorical_data}

    test_row = pd.DataFrame(data_dict)
# for index, label in enumerate(category_labels):
        # if(selections[index]=='Unknown'):
        #     selections[index] = df[label].mode()
        # for col in list(filter(lambda c : label in c,categorical_features)):
        #     test_row[col] = 1 if col == f'{label}_{selections[index]}' else 0
    # Perform input validation (customize as needed)
    # if (
    #     user_kms_driven <= 0
    #     or user_car_age < 0
    #     or user_engine_capacity < 0
    #     or user_seats < 0
    #     or user_model_year <= 2002 or user_model_year > 2023
    #     or user_mileage < 0
    #     or user_max_power < 0
    # ):
    #     sl.warning("Please enter valid numeric values for the input fields.")
    #     return
    print(numerical_data)
    with open('data/xgb_model.pkl', 'rb') as file:
        loaded_model = pkl.load(file)
    # Perform prediction using your resale_predictor model (replace this with your actual prediction logic)
    predicted_price = loaded_model.predict(test_row) # Replace with actual prediction logic

    sl.subheader('Prediction Result')
    sl.write(f"Predicted resale price: Rs {numerize(Decimal(str(predicted_price[0])))}")

def sideBar():
 with sl.sidebar:
    selected=option_menu(
        menu_title="Main Menu",
        options=["Home","Price Genie", "Price Predictor"],
        icons=["house","eye"],
        menu_icon="cast",
        default_index=0,
    )
 if selected=="Price Genie":
    Add_Analytic_Filters()
    Progressbar()
    graphs()
 elif selected=="Price Predictor":
    Predict()
 else:
    Add_Analytic_Filters()
    Home()
    graphs()
    Plot_QuantitaveData_Trends()

sideBar()

# sl.dataframe(df_s)

#theme
hide_st_style=""" 

<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
