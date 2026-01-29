import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from astropy.io import ascii


st.title("Magneto Models")

st.write("This displays the velocity vs flux data from magnetospheric accretion models.")

@st.cache_data
def load_ids():
    data = pd.read_csv('magnetomodels-ids.csv')
    return data
mag_ids = load_ids()

mdots = {'M01':{'val':1.00e-7,'tmin':0,'tmax':8  },\
         'M02':{'val':5.62e-8,'tmin':0,'tmax':8  },\
         'M03':{'val':3.16e-8,'tmin':0,'tmax':8  },\
         'M04':{'val':1.78e-8,'tmin':0,'tmax':8  },\
         'M05':{'val':1.00e-8,'tmin':1,'tmax':12 },\
         'M06':{'val':5.62e-9,'tmin':1,'tmax':12 },\
         'M07':{'val':3.16e-9,'tmin':1,'tmax':12 },\
         'M08':{'val':1.78e-9,'tmin':1,'tmax':12 },\
         'M09':{'val':1.00e-9,'tmin':4,'tmax':16 },\
         'M10':{'val':5.62e-10,'tmin':4,'tmax':16 },\
         'M11':{'val':3.16e-10,'tmin':4,'tmax':16 },\
         'M12':{'val':1.78e-10,'tmin':4,'tmax':16 },\
         'M13':{'val':1.00e-10,'tmin':4,'tmax':16 },\
         'M15':{'val':1.78e-7,'tmin':0,'tmax':8 },\
         'M14':{'val':3.16e-7,'tmin':0,'tmax':8 },\
         }

temps_list = mag_ids['Tmax'][~np.isnan(mag_ids['Tmax'])].unique()
# print(temps_list)
mdot_list = mag_ids['Mdot'][~np.isnan(mag_ids['Mdot'])].unique()
# print(mdot_list)

lines = {'h23':r"Hα",
         'h24':r"Hβ", 
         'ca15':r"Ca II K",
         }

abundances = {'.Ca':r"Solar",
            '.Ca_0p5':r"50% Solar", 
            '.Ca_0p1':r"10% Solar",
            '.Ca_0p01':r"1% Solar",
            }

# temps_ = temps[mdots[md]['tmin']:mdots[md]['tmax']]
line = st.selectbox('Select line', format_func=lambda x: lines[x], options=list(lines.keys()))
Mdot = st.selectbox('Select Mdot', mdot_list)
mdot_idx = np.where(mdot_list  == Mdot)



with st.form("my_form"):
    st.write("Parameter selection")

    Tmax = st.selectbox('Select Tmax', temps_list[mdots[f'M{mdot_idx[0][0]+1:02d}']['tmin']:mdots[f'M{mdot_idx[0][0]+1:02d}']['tmax']])
    Rin = st.selectbox('Select Rin', mag_ids['Rin'][~np.isnan(mag_ids['Rin'])].unique())
    width = st.selectbox('Select width', mag_ids['Width'][~np.isnan(mag_ids['Width'])].unique())

    inc= st.selectbox('Select inclination', [15,30,45,60,75])

    if line == 'ca15':
        abund = st.selectbox('Select Ca abundance',format_func=lambda x: abundances[x], options=list(abundances.keys()))
    else:
        abund = ''
    st.form_submit_button('Submit my picks')

tmax_idx = np.where(temps_list == Tmax)[0][0]+1

# print(Rin)
# print(width)
#We wanr the index where the mags_id row has the combination of Ri and width
geo_idx = mag_ids[ (mag_ids['Rin'] == Rin) & (mag_ids['Width'] == width)]['ID'].values[0]
print(geo_idx)


file_name = f'prof.{line}{abund}.G{geo_idx:02d}.M{mdot_idx[0][0]+1:02d}.T{tmax_idx:02d}.I{int(inc)}.0'
print(file_name)