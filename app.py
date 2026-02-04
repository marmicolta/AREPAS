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
# DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")

# if DROPBOX_TOKEN is None:
#     raise RuntimeError(
#         "DROPBOX_TOKEN not found. "
#         "Create a .env file with your Dropbox access token."
#     )

# dbx = dropbox.Dropbox(DROPBOX_TOKEN)
dbx = dropbox.Dropbox(
    oauth2_refresh_token=os.environ["DROPBOX_REFRESH_TOKEN"],
    app_key=os.environ["DROPBOX_APP_KEY"],
    app_secret=os.environ["DROPBOX_APP_SECRET"],
)

# --------- Page Title ---------- #
st.set_page_config(layout="wide")

st.title("Magneto Models")

st.write("This displays the velocity vs flux data from magnetospheric accretion models.")

with st.expander("How to use this app"):
    st.write('''
    This app allows users to explore magnetospheric accretion line profile models for different spectral lines, 
             mass accretion rates, maximum temperatures, disk geometries, inclinations, and abundances. 
             Select model parameters from the sidebar to visualize how they affect the line profiles. 
             Multiple models can be overplotted for comparison. Data files are fetched from Dropbox 
             as needed and cached locally for faster access. 
    ''')
    st.markdown("### Instructions:")
    st.markdown("1. Use the sidebar to select model parameters")
    st.markdown("2. Click 'Submit' to add the selected model to the dataframe. \n")
    st.markdown("3. Select *one* row in the data table by clicking the checkbox in the first column to visualize the corresponding line profiles. Select *all* rows by clicking the checkbox in the header of the first column. \n")
    st.markdown("4. Use the 'Clear Data' button to reset selections.""")
    st.markdown("The plot has an interactive legend and zooming capabilities. Click on legend entries to toggle visibility of specific models. Click and drag on the plot area to zoom in on regions of interest. Double-click to reset the zoom.")
    st.markdown("To download the raw data for all the models you have selected, click on the graph symbol at the top-right corner of the plot and then click the down arrow in the top-right corner that will let you 'Download as CSV'.")
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
         'h25':r"Hγ",
         'h35':r"Paβ",
         'h36':r"Paγ",
         'h37':r"Paδ",
         'h47':r"Brγ",
         'ca15':r"Ca II K",
         'ca25':r"Ca II 8498",
         'ca35':r"Ca II 8542",
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

# --- button to clear the dataframe ---
def clear_data():
    st.session_state.data = pd.DataFrame({'line':[],'Mdot':[],'Tmax':[],'Rin':[], 'Width':[], 'Inclination':[], 'Abundance':[], "Spectral Type":[]})
    st.session_state.all_data = pd.DataFrame({'Velocity':[], 'Flux':[], 'Nflux':[], 'Label':[]})
st.button('Clear Data', on_click=clear_data, help='Clears all selected model parameters and plotted data.')

# if 'all_data' not in st.session_state:
#     all_data = pd.DataFrame({'Velocity':[], 'Flux':[], 'Nflux':[], 'Label':[]})
#     st.session_state.all_data = all_data


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

        # get_flux_data()
    # st.session_state.data = pd.concat([st.session_state.data, row], ignore_index=True)



# --------- Sidebar for parameter selection ---------- #
with st.sidebar:
    # Inputs created outside of a form (allows computing col4 for preview)

    st.header('Model Parameter Selection')

    line = st.selectbox('Select line', format_func=lambda x: lines[x], options=list(lines.keys()), key='line', help='Which spectral line to model.')

    Mdot = st.selectbox('Select Mdot', mdot_list, key='Mdot', help='The mass accretion rate in solar masses per year.')
    mdot_idx = np.where(mdot_list  == Mdot)


    Tmax = st.selectbox('Select Tmax', temps_list[mdots[f'M{mdot_idx[0][0]+1:02d}']['tmin']:mdots[f'M{mdot_idx[0][0]+1:02d}']['tmax']] , key='Tmax', help='The maximum temperature in Kelvin.')
    
    Rin = st.selectbox('Select Rin', np.sort(mag_ids['Rin'][~np.isnan(mag_ids['Rin'])].unique()), key='Rin', help='The inner radius of the disk in stellar radii.')

    width = st.selectbox('Select width', np.sort(mag_ids['Width'][~np.isnan(mag_ids['Width'])].unique()), key='Width', help='The width of the disk in stellar radii.')

    inc= st.selectbox('Select inclination', [15,30,45,60,75], key='Inclination', help='The inclination angle of the disk in degrees.')
    if line == 'ca15':

        # print(abundances.keys())
        if st.session_state.get('abund') is None:
            st.session_state.abund = list(abundances.keys())[0]
        abund = st.selectbox('Select Ca abundance',format_func=lambda x: abundances[x], options=list(abundances.keys()), key='abund', placeholder='Ca', help='The Calcium abundance.', )
    else:

        # abund = st.selectbox('Select Ca abundance',options=['h'], key='abund', disabled=True, placeholder='')
        abund= ""
        st.session_state.abund = ""
        # st.form_submit_button('Submit my picks')

    spectral_type = st.selectbox('Select Spectral Type', ['M1','M3','M5','K2','K5','K7'], key='spectral_type', help='The spectral type of the star.')
    #                     disabled=True)
    st.button('Submit', on_click=add_df)

# Show current data
# df = st.dataframe(st.session_state.data, width='content', on_select='rerun', selection_mode='multi-row')
event = st.dataframe(st.session_state.data, width='stretch', on_select='rerun', selection_mode='multi-row')

#--------- Get data model from dropbox ---------- #
CACHE_DIR = Path.home() / ".cache" / "magnetomodels"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Function to get model file from dropbox
def get_model_file(fname,spt,line):
    
    # # Check if file exists in cache
    # local_path = CACHE_DIR / f"{spt}.{fname}"
    # # If not, download it from dropbox
    # if not local_path.exists():
    #     # print(spt)
    #     print(f"/Profiles/{spt}profiles/{fname}")
    #     download_from_dropbox(f"/Profiles/{spt}profiles/{fname}", local_path)
    url = f"https://raw.githubusercontent.com/marmicolta/data_magneto_models/refs/heads/main/{spt}profiles/{line}/{fname}"
    return url


# # Function to download file from dropbox and save to local path
# def download_from_dropbox(remote_path, local_path):
#     print(f"Downloading {remote_path} from Dropbox...")

#     md, res = dbx.files_download(remote_path)

#     with open(local_path, "wb") as f:
#         f.write(res.content)




@st.cache_data
def load_data(file_name,spectral_type,line):
    # data = ascii.read('models/K7/'+file_name, names=['Velocity','Flux'])
    print(get_model_file(file_name,spectral_type,line))
    data = ascii.read(get_model_file(file_name,spectral_type,line), names=['Velocity','Flux'])

    return data

# --------- find the indices for file naming ---------- #
# Store each profile's data in a list for overplotting
# if 'profiles' not in st.session_state:
#     st.session_state.profiles = []

# get list of filenames from pandas dataframe
# print(st.session_state.data.keys())
# all_data = pd.DataFrame()
# st.dataframe(st.session_state.data)
# st.dataframe(st.session_state.all_data)
normalize_flux = st.checkbox('Normalize Flux', value=False, help='If checked, the flux will be normalized so the continuum level has a value of 1.')
hide_legend = st.checkbox('Hide Legend', value=False, help='If checked, the legend will be hidden from the plot.')
def get_flux_data():
    rows = event.selection.rows
    filtered_df = st.session_state.data.iloc[rows]
    # st.dataframe(filtered_df)
    st.session_state.all_data = pd.DataFrame({'Velocity':[], 'Flux':[], 'Nflux':[], 'Label':[]})
    # for row in st.session_state.data.itertuples():
    for row in filtered_df.itertuples():
        # print(row)
        # line = row.line
        # Mdot = row.Mdot
        # Tmax = row.Tmax
        # Rin = row.Rin
        # width = row.Width
        # inc = row.Inclination
        abundance = row.Abundance
        if abundance==None:
            abundance = ""
        spectype = row._8
        mdot_idx = np.where(mdot_list  == row.Mdot)
        tmax_idx = np.where(temps_list == row.Tmax)[0][0]+1

        # print(Rin)
        # print(width)
        #We wanr the index where the mags_id row has the combination of Ri and width
        geo_idx = mag_ids[ (mag_ids['Rin'] == row.Rin) & (mag_ids['Width'] == row.Width)]['ID'].values[0]
        # print(geo_idx)


        file_name = f'prof.{row.line}{abundance}.G{geo_idx:02d}.M{mdot_idx[0][0]+1:02d}.T{tmax_idx:02d}.I{int(row.Inclination)}.0'
        # print(file_name)
        # files_to_plot.append((file_name, spectral_type))

        # Load the data
        profdata = load_data(file_name,spectype,row.line)
        vel = profdata['Velocity'].data
        fnu = profdata['Flux'].data
        v1,v2 = vel[0], vel[-1]
        f1,f2 = fnu[0],fnu[-1]

        m = (f2-f1)/(v2-v1)
        f_cont = m * (vel-v1) + f1

        Nflux = fnu/f_cont

        pandas_data = profdata.to_pandas()
        pandas_data['Nflux'] = Nflux

        # print(normalize_flux)
        # if normalize_flux:
            # data['Flux'] = data['Flux']/np.max(data['Flux'])
        # pandas_data['NFlux'] = Nflux
        #     flux_label = 'Normalized Fν'
        # else:
        #     flux_label = r'Fν (erg/s/cm²/Hz)'



        # profile_df = pandas_data[['Velocity', 'Flux']].copy()
        # pandas_data['Label'] = f"{lines[row.line]}, Mdot={row.Mdot:.2e}, Tmax={row.Tmax}, Rin={row.Rin}, Width={row.Width}, Inc={row.Inclination}, Spt={spectype}, Abund={abundance}"
        pandas_data['Label'] = f"{lines[row.line]}|{row.Mdot:.2f}|{row.Tmax:.0f}|{row.Rin}|{row.Width}|{row.Inclination:.0f}|{spectype}|{abundance}"

        pandas_data['Label'] = pandas_data['Label'].str.replace('.Ca',' Ca Solar').str.replace('_0p5',' 50% Solar').str.replace('_0p1',' 10% Solar').str.replace('_0p01',' 1% Solar')
        # st.session_state.data = pd.concat([st.session_state.data, row], ignore_index=True)

        st.session_state.all_data = pd.concat([st.session_state.all_data, pandas_data], ignore_index=True)
        # print(profile_df)
        # st.session_state.profiles.append(profile_df)

# st.dataframe(st.session_state.all_data)
get_flux_data()

if normalize_flux:
    flux_label = 'Normalized Fν'
    flux_param = 'Nflux'
else:
    flux_label = r'Fν (erg/s/cm²/Hz)'
    flux_param = 'Flux'

# print(st.session_state.all_data)

# print(st.session_state.profiles)
# --------- plotting the models ---------- #

if not st.session_state.all_data.empty:

    selection = alt.selection_point(fields=['Label'], bind='legend')
    selection_zoom = alt.selection_interval(bind='scales', empty='all')
    if hide_legend:
        # selection = alt.selection_point(fields=['Label'], bind=None)
        legend=None
    else:
        legend=alt.Legend(title="Models", labelLimit=400, direction="vertical", orient="right", columns=1)
    chart1 = alt.Chart(st.session_state.all_data).mark_point().encode(
        x=alt.X('Velocity', title='Velocity (km/s)'),
        y=alt.Y(flux_param, title=flux_label),
        color=alt.Color('Label:N', legend=legend),
        tooltip=['Velocity', flux_param, 'Label'],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.0) ),
        ).properties(
        # title=f'Line Profile: {lines[line]}, Mdot={Mdot:.2e} Msun/yr, Tmax={Tmax}K, Rin={Rin}R*, Width={width}R*, Inc={inc}°',
        width=700,
        height=400,
        # tooltip=['Velocity','Flux']
        )

    chart2 = alt.Chart(st.session_state.all_data).mark_line().encode(
        x=alt.X('Velocity', title='Velocity (km/s)'),
        y=alt.Y(flux_param, title=flux_label),
        color='Label:N',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.0) ),
        ).properties(
        # title=f'Line Profile: {lines[line]}, Mdot={Mdot:.2e} Msun/yr, Tmax={Tmax}K, Rin={Rin}R*, Width={width}R*, Inc={inc}°',
        width=700,
        height=400,

        )

    chart = chart1 + chart2
    chart = chart.add_params(selection, selection_zoom)

    # zoom_pan = alt.selection_interval(bind='scales')
    st.altair_chart(chart, width='stretch', )

# --------- let user download data ---------- #

# st.download_button(
#     label="Download data as CSV",
#     data=pandas_data.to_csv(index=False).encode('utf-8'),
#     file_name=f'{file_name}.csv',
#     mime='text/csv',
# )

# --------- footer ---------- #

with st.container():

    st.markdown("App made with :heart: and :sparkles: by [Marbely Micolta](https://sites.google.com/umich.edu/marbelymicolta?usp=sharing) & [Katya Gozman](https://kgozman6159.github.io/) using Streamlit :streamlit:, python, Altair, and Pandas.")    
    st.markdown("Magnetospheric Accretion Model References: [Hartmann et al. (1994)](https://ui.adsabs.harvard.edu/abs/1994ApJ...426..669H/abstract), [Muzerolle et al. (2001)](https://ui.adsabs.harvard.edu/abs/2001ApJ...550..944M/abstract)")
    st.markdown("Model grid generated by [Marbely Micolta](https://sites.google.com/umich.edu/marbelymicolta?usp=sharing) and [Thanawuth (Atom) Thanathibodee](https://www.frontier.phys.sc.chula.ac.th/thanawut-w).")

    st.divider()
    st.markdown("Related Papers:")
    # st.markdown("- Patiño et al. (2026),in review")
    st.markdown("- [Micolta et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...976..251M/abstract)")
    st.markdown("- [Micolta et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...953..177M/abstract)")
    st.markdown("- [Thanathibodee et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...944...90T/abstract)")
    st.markdown("- [Thanathibodee et al. (2020)](https://ui.adsabs.harvard.edu/abs/2020ApJ...892...81T/abstract)")
    st.markdown("- [Thanathibodee et al. (2019)](https://ui.adsabs.harvard.edu/abs/2019ApJ...884...86T/abstract)")




# --------- Clear cache button ---------- #
st.sidebar.header("Clear Cache")
if st.sidebar.button("Clear Cached Data", help="Clears all cached data files from your local machine."):
    
    shutil.rmtree(CACHE_DIR)  # deletes the folder and all contents