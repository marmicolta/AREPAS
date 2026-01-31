import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import ascii
import altair as alt

from pathlib import Path
from dotenv import load_dotenv
import dropbox
import os
import shutil

# --------- Dropbox API setup ---------- #
# .env should be in gitignore but really not gonna make Nuria figure out APIs

load_dotenv()  # reads .env automatically. 
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")

if DROPBOX_TOKEN is None:
    raise RuntimeError(
        "DROPBOX_TOKEN not found. "
        "Create a .env file with your Dropbox access token."
    )

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# --------- Page Title ---------- #

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

# Create an empty dataframe on first page load, will skip on page reloads
if 'data' not in st.session_state:
    data = pd.DataFrame({'line':[],'Mdot':[],'Tmax':[],'Rin':[], 'Width':[], 'Inclination':[], 'Abundance':[], "Spectral Type":[]})
    st.session_state.data = data

# Show current data
st.dataframe(st.session_state.data)

# Function to append non-form inputs into dataframe
def add_df():
    row = pd.DataFrame({'line':[st.session_state.line],
            'Mdot':[st.session_state.Mdot],
            'Tmax':[st.session_state.Tmax],
            'Rin':[st.session_state.Rin],
            'Width':[st.session_state.Width],
            'Inclination':[st.session_state.Inclination],
            'Abundance':[st.session_state.abund],
            "Spectral Type":[st.session_state.spectral_type]})
    # Check if the row already exists in the dataframe
    exists = ((st.session_state.data['line'] == st.session_state.line) &
              (st.session_state.data['Mdot'] == st.session_state.Mdot) &
              (st.session_state.data['Tmax'] == st.session_state.Tmax) &
              (st.session_state.data['Rin'] == st.session_state.Rin) &
              (st.session_state.data['Width'] == st.session_state.Width) &
              (st.session_state.data['Inclination'] == st.session_state.Inclination) &
              (st.session_state.data['Abundance'] == st.session_state.abund) &
              (st.session_state.data['Spectral Type'] == st.session_state.spectral_type)).any()
    if not exists:
        st.session_state.data = pd.concat([st.session_state.data, row], ignore_index=True)
    # st.session_state.data = pd.concat([st.session_state.data, row], ignore_index=True)



# --------- Sidebar for parameter selection ---------- #
with st.sidebar:
    # Inputs created outside of a form (allows computing col4 for preview)
    # dfColumns = st.columns(8)
    st.header('Model Parameter Selection')
    # with dfColumns[0]:
    line = st.selectbox('Select line', format_func=lambda x: lines[x], options=list(lines.keys()), key='line')
    # with dfColumns[1]:
    Mdot = st.selectbox('Select Mdot', mdot_list, key='Mdot')
    mdot_idx = np.where(mdot_list  == Mdot)



    # with st.form("my_form"):
    # st.write("Parameter selection")
    # with dfColumns[2]:
    Tmax = st.selectbox('Select Tmax', temps_list[mdots[f'M{mdot_idx[0][0]+1:02d}']['tmin']:mdots[f'M{mdot_idx[0][0]+1:02d}']['tmax']] , key='Tmax')
    # with dfColumns[3]:
    Rin = st.selectbox('Select Rin', mag_ids['Rin'][~np.isnan(mag_ids['Rin'])].unique(), key='Rin')
    # with dfColumns[4]:
    width = st.selectbox('Select width', mag_ids['Width'][~np.isnan(mag_ids['Width'])].unique(), key='Width')
    # with dfColumns[5]:
    inc= st.selectbox('Select inclination', [15,30,45,60,75], key='Inclination')

    if line == 'ca15':
        # with dfColumns[6]:
        print(abundances.keys())
        if st.session_state.get('abund') is None:
            st.session_state.abund = list(abundances.keys())[0]
        abund = st.selectbox('Select Ca abundance',format_func=lambda x: abundances[x], options=list(abundances.keys()), key='abund', placeholder='Ca')
    else:
        # with dfColumns[6]:
        # abund = st.selectbox('Select Ca abundance',options=['h'], key='abund', disabled=True, placeholder='')
        abund= ""
        st.session_state.abund = ""
        # st.form_submit_button('Submit my picks')
    # with dfColumns[7]:
    spectral_type = st.selectbox('Select Spectral Type', ['M1','M3','M5','K2','K5','K7'], key='spectral_type')
    #                     disabled=True)
    st.button('Submit', on_click=add_df)



#--------- Get data model from dropbox ---------- #
CACHE_DIR = Path.home() / ".cache" / "magnetomodels"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Function to get model file from dropbox
def get_model_file(fname,spt):
    
    # Check if file exists in cache
    local_path = CACHE_DIR / f"{spt}.{fname}"
    # If not, download it from dropbox
    if not local_path.exists():
        print(spt)
        print(f"/Profiles/{spt}profiles/{fname}")
        download_from_dropbox(f"/Profiles/{spt}profiles/{fname}", local_path)

    return local_path


# Function to download file from dropbox and save to local path
def download_from_dropbox(remote_path, local_path):
    print(f"Downloading {remote_path} from Dropbox...")

    md, res = dbx.files_download(remote_path)

    with open(local_path, "wb") as f:
        f.write(res.content)




@st.cache_data
def load_data(file_name,spectral_type):
    # data = ascii.read('models/K7/'+file_name, names=['Velocity','Flux'])
    data = ascii.read(get_model_file(file_name,spectral_type), names=['Velocity','Flux'])

    return data

# --------- find the indices for file naming ---------- #
# Store each profile's data in a list for overplotting
# if 'profiles' not in st.session_state:
#     st.session_state.profiles = []

# get list of filenames from pandas dataframe
# print(st.session_state.data.keys())
normalize_flux = st.checkbox('Normalize Flux', value=False)
files_to_plot = []
for row in st.session_state.data.itertuples():
    # print(row)
    line = row.line
    Mdot = row.Mdot
    Tmax = row.Tmax
    Rin = row.Rin
    width = row.Width
    inc = row.Inclination
    abund = row.Abundance
    if abund==None:
        abund = ""
    spectral_type = row._8
    


    tmax_idx = np.where(temps_list == Tmax)[0][0]+1

    # print(Rin)
    # print(width)
    #We wanr the index where the mags_id row has the combination of Ri and width
    geo_idx = mag_ids[ (mag_ids['Rin'] == Rin) & (mag_ids['Width'] == width)]['ID'].values[0]
    print(geo_idx)


    file_name = f'prof.{line}{abund}.G{geo_idx:02d}.M{mdot_idx[0][0]+1:02d}.T{tmax_idx:02d}.I{int(inc)}.0'
    print(file_name)
    files_to_plot.append((file_name, spectral_type))

    # Load the data
    profdata = load_data(file_name,spectral_type)
    vel = profdata['Velocity'].data
    fnu = profdata['Flux'].data
    v1,v2 = vel[0], vel[-1]
    f1,f2 = fnu[0],fnu[-1]

    # m = (f2-f1)/(v2-v1)
    # f_cont = m * (vel-v1) + f1

    # Nflux = fnu/f_cont

    # pandas_data = data.to_pandas()
    # pandas_data['Nflux'] = Nflux

    
    # if normalize_flux:
    #     # data['Flux'] = data['Flux']/np.max(data['Flux'])
    #     data['Flux'] = Nflux
    #     flux_label = 'Normalized Fν'
    # else:
    #     flux_label = r'Fν (erg/s/cm²/Hz)'



    # # profile_df = pandas_data[['Velocity', 'Flux']].copy()
    # pandas_data['Label'] = f"{lines[line]}, Mdot={Mdot:.2e}, Tmax={Tmax}, Rin={Rin}, Width={width}, Inc={inc}, Spt={spectral_type}"
    # print(profile_df)
    # st.session_state.profiles.append(profile_df)


# print(st.session_state.profiles)
# --------- plotting the models ---------- #

# chart1 = alt.Chart(data).mark_point().encode(
#     x=alt.X('Velocity', title='Velocity (km/s)'),
#     y=alt.Y('Flux', title=flux_label),
#     ).properties(
#     title=f'Line Profile: {lines[line]}, Mdot={Mdot:.2e} Msun/yr, Tmax={Tmax}K, Rin={Rin}R*, Width={width}R*, Inc={inc}°',
#     width=700,
#     height=400,
#     # tooltip=['Velocity','Flux']
#     )   

# chart2 = alt.Chart(data).mark_line().encode(
#     x=alt.X('Velocity', title='Velocity (km/s)'),
#     y=alt.Y('Flux', title=flux_label),
#     ).properties(
#     title=f'Line Profile: {lines[line]}, Mdot={Mdot:.2e} Msun/yr, Tmax={Tmax}K, Rin={Rin}R*, Width={width}R*, Inc={inc}°',
#     width=700,
#     height=400,

#     )   

# chart = chart1 + chart2
# chart = chart.interactive()

# # zoom_pan = alt.selection_interval(bind='scales')
# st.altair_chart(chart, width='stretch')

# --------- let user download data ---------- #

# st.download_button(
#     label="Download data as CSV",
#     data=pandas_data.to_csv(index=False).encode('utf-8'),
#     file_name=f'{file_name}.csv',
#     mime='text/csv',
# )

# --------- footer ---------- #

with st.container():

    st.markdown("Made with :heart: and :sparkles: by Marbely Micolta & Katya Gozman using Streamlit :streamlit:, python, Altair, and Pandas.")    
    st.markdown("Model References: [Hartmann et al. (1994)](https://ui.adsabs.harvard.edu/abs/1994ApJ...426..669H/abstract), [Muzerolle et al. (2001)](https://ui.adsabs.harvard.edu/abs/2001ApJ...550..944M/abstract)")


# --------- Clear cache button ---------- #
st.sidebar.header("Clear Cache")
if st.sidebar.button("Clear Cached Data"):
    
    shutil.rmtree(CACHE_DIR)  # deletes the folder and all contents