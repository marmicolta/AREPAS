import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import ascii


st.title("Magneto Models")

st.write("This displays the velocity vs flux data from magnetospheric accretion models.")

@st.cache_data
def load_ids():
    data = pd.read_csv('magnetomodels-ids.csv')
    return data
mag_ids = load_ids()


with st.form("my_form"):
   st.write("Parameter selection")
   Tmax = st.selectbox('Select Tmax', mag_ids['Tmax'][~np.isnan(mag_ids['Tmax'])].unique())
   Mdot = st.selectbox('Select Mdot', mag_ids['Mdot'][~np.isnan(mag_ids['Mdot'])].unique())
   Rin = st.selectbox('Select Rin', mag_ids['Rin'][~np.isnan(mag_ids['Rin'])].unique())
   width = st.selectbox('Select width', mag_ids['Width'][~np.isnan(mag_ids['Width'])].unique())
   st.form_submit_button('Submit my picks')



