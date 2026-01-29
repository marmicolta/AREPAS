import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import ascii
import altair as alt

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

@st.cache_data
def load_data(file_name):
    data = ascii.read('models/K7/'+file_name, names=['Velocity','Flux'])
    return data


# def read_mod_profile(ID):

#     try:
#         model_data = ascii.read(f'{path_mod}/prof.h23.{ID}.0', names=['velocity', 'flux'])
#     except FileNotFoundError:
#         print('file model not found')
#         return -999.0, -999.0, -999.0
    
#     vel = model_data['velocity'].data
#     fnu = model_data['flux'].data

#     v1,v2 = vel[0], vel[-1]
#     f1,f2 = fnu[0],fnu[-1]

#     m = (f2-f1)/(v2-v1)
#     f_cont = m * (vel-v1) + f1
    
#     Nflux = fnu/f_cont
    
#     return vel, Nflux 


data = load_data(file_name)
vel = data['Velocity'].data
fnu = data['Flux'].data
v1,v2 = vel[0], vel[-1]
f1,f2 = fnu[0],fnu[-1]

m = (f2-f1)/(v2-v1)
f_cont = m * (vel-v1) + f1

Nflux = fnu/f_cont

pandas_data = data.to_pandas()
pandas_data['Nflux'] = Nflux

normalize_flux = st.checkbox('Normalize Flux', value=False)
if normalize_flux:
    # data['Flux'] = data['Flux']/np.max(data['Flux'])
    data['Flux'] = Nflux
    flux_label = 'Normalized Fν'
else:
    flux_label = r'Fν (erg/s/cm²/Hz)'

chart1 = alt.Chart(data.to_pandas()).mark_point().encode(
    x=alt.X('Velocity', title='Velocity (km/s)'),
    y=alt.Y('Flux', title=flux_label),
    ).properties(
    title=f'Line Profile: {lines[line]}, Mdot={Mdot:.2e} Msun/yr, Tmax={Tmax}K, Rin={Rin}R*, Width={width}R*, Inc={inc}°',
    width=700,
    height=400,
    # tooltip=['Velocity','Flux']
    )   

chart2 = alt.Chart(data.to_pandas()).mark_line().encode(
    x=alt.X('Velocity', title='Velocity (km/s)'),
    y=alt.Y('Flux', title=flux_label),
    ).properties(
    title=f'Line Profile: {lines[line]}, Mdot={Mdot:.2e} Msun/yr, Tmax={Tmax}K, Rin={Rin}R*, Width={width}R*, Inc={inc}°',
    width=700,
    height=400,

    )   

chart = chart1 + chart2
chart = chart.interactive()

# zoom_pan = alt.selection_interval(bind='scales')
st.altair_chart(chart, use_container_width=True)

st.download_button(
    label="Download data as CSV",
    data=pandas_data.to_csv(index=False).encode('utf-8'),
    file_name=f'{file_name}.csv',
    mime='text/csv',
)

with st.container():

    st.markdown("Made with :heart: and :sparkles: by Marbely Micolta & Katya Gozman using Streamlit :streamlit:, python, Altair, and Pandas.")    
    st.markdown("Model References: [Hartmann et al. (1994)](https://ui.adsabs.harvard.edu/abs/1994ApJ...426..669H/abstract), [Muzerolle et al. (2001)](https://ui.adsabs.harvard.edu/abs/2001ApJ...550..944M/abstract)")
