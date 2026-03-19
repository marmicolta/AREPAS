import streamlit as st
import numpy as np
import pandas as pd
from astropy.io import ascii
import altair as alt
import astropy.units as u
from astropy.constants import c
from astropy.constants import L_sun
import matplotlib.colors as mcolors

st.set_page_config(layout="wide",
    page_title="AREPAS",
    page_icon="🫓",
    initial_sidebar_state="expanded",
    menu_items={
    'Report a bug': "https://github.com/marmicolta/AREPAS/issues",
    'About':"If you have any feature requests or find any bugs, please report them on the [GitHub](https://github.com/marmicolta/AREPAS/issues) page or contact us at micoltam [at] umich [dot] edu or kgozman [at] umich [dot] edu"""
  })


def get_flux(flux, vel, line):
    
    ve = vel*u.km/u.s
    freq = 1e9*c/(line_centers[line]*u.m)
    nu = -1.0 * ve/(c.to('km/s')) * freq + freq
    fnu = flux*(u.erg/(u.cm*u.cm*u.s*u.Hz))
                    
    # approximate the continuum with a linear function
    nu1, nu2 = nu[0], nu[-1]
    fnu1, fnu2 = fnu[0], fnu [-1]
    m = (fnu2 - fnu1) / (nu2 - nu1)
    fnu_con = m * (nu - nu1) + fnu1
                    
    #Flux continuum substracted
    fluxvsel = (fnu - fnu_con).value
                        
    #Flux in emission
    fluxpos = [0 if b < 0 else b for b in fluxvsel]
    flux_line = (-1.0 * np.trapezoid(fluxpos, nu))
                    
    # #Flux in absorption
    # fluxneg = [0 if b > 0 else b for b in fluxvsel]
    # flux_abs = (-1.0 * np.trapz(fluxneg, nu))
    
    # return fluxpos, flux_line, flux_abs, fluxneg
    return flux_line


#--------- Get data model from Github---------- #

# Function to get model file from dropbox
def get_model_file(fname,spt,line):
    
    url = f"https://raw.githubusercontent.com/marmicolta/data_magneto_models/refs/heads/main/{spt}profiles/{line}/{fname}"
    return url


@st.cache_data
def load_data(file_name,spectral_type,line):
    # data = ascii.read('models/K7/'+file_name, names=['Velocity','Flux'])
    print(get_model_file(file_name,spectral_type,line))
    data = ascii.read(get_model_file(file_name,spectral_type,line), names=['Velocity','Flux'])

    return data


# --------- Page Title and Intro ---------- #
st.set_page_config(layout="wide")

st.title("AREPAS🫓: A Resource for Exploring Protostellar Accretion Systems")

st.write("Welcome to AREPAS🫓,")
st.write("This is a visualization tool for the [Open Library of Magnetospheric Accretion Models for T Tauri stars](https://github.com/marmicolta/database_magneto_models) [![DOI](https://zenodo.org/badge/1144882498.svg)](https://doi.org/10.5281/zenodo.18852909) ")
with st.expander("How to use this app"):
    st.write('''
    This app allows users to explore magnetospheric accretion line profile models for different spectral lines, 
             mass accretion rates, maximum temperatures, disk geometries, inclinations, and abundances. 
             Select model parameters from the sidebar to visualize how they affect the line profiles. 
             Multiple models can be overplotted for comparison. You can also upload your own file with an observed profile to compare to the models.
            Data files are fetched from Github 
             as needed and cached locally for faster access. 
    ''')
    st.markdown("### Instructions:")
    st.markdown("1. Use the sidebar to select model parameters.")
    st.markdown("2. Click 'Submit' to add the selected model to the dataframe. \n")
    st.markdown("""3. To upload your own data, click 'Browse files' in the sidebar and select a CSV file where the first three columns are velocity (in km/s), flux (in erg/s/cm²/Å), and distance (in pc). Other columns will be ignored.
                The distance column needs to just have the first cell with the distance, all other cells may be left blank (they will be ignored); it will be used to compute the line luminosity, as calculated by L=4πd²F, if needed. Then click 'Submit' to add it to the dataframe. \n""")
    st.markdown("""4. Select *one* row in the data table by clicking the checkbox in the first column to visualize the corresponding line profiles. Select *all* rows by clicking the checkbox in the header of the first column. 
                    \n      * Use the buttons to choose what to plot on the y-axis. 'Flux' will be the flux in erg/s/cm²/Å. 'Normalized Flux' will be flux normalized to the continuum.
                 "Luminosity" will be the luminosity in erg/s. For the models, this is calculated by L=4πR²F, where F is the flux at the surface of the star and R is the radius of a star of the specified spectral type. 
                If comparing with observed data, it is recommended to use normalized flux or luminosity values as the model fluxes are calculated at the surface of the star.\n""")
    st.markdown("5. Use the 'Clear Data' button to reset selections.")
    st.markdown("The plot has an interactive legend and zooming capabilities. Click on legend entries to toggle visibility of specific models. Click and drag on the plot area to zoom in on regions of interest. Double-click to reset the zoom.")
    st.markdown('You can change the color scheme of the app by toggling between light and dark mode in the settings (top-right corner hamburger menu -> Settings). The color gradients in the dataframe will adjust accordingly to help differentiate between parameter values.')
    st.markdown("To download the raw data for all the models you have selected, click on the graph symbol at the top-right corner of the plot and then click the down arrow in the top-right corner that will let you 'Download as CSV'.")

@st.cache_data
def load_ids():
    # --- loads in supplementary file with model parameters, which is used to find the correct file name for a given set of parameters --- #
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

mdot_list = mag_ids['Mdot'][~np.isnan(mag_ids['Mdot'])].unique()


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

line_centers = {'h23':656.279, \
         'h24':486.135, \
         'h25':434.0472,\
         'h35':1281.8072, \
         'h36':1093.8086, \
         'h37':1004.9369, \
         'h47':2166.121,\
         'ca15':393.4, \
         'ca25':849.802, \
         'ca35':854.209,
         'mg12':280.367
        }     



# Create an empty dataframe on first page load, will skip on page reloads
if 'data' not in st.session_state:
    data = pd.DataFrame({'line':[], 'Line':[], 'Mdot':[],'Tmax':[],'Rin':[], 'Width':[], 'Inclination':[], 'Abundance':[], "SpectralType":[], "Int_Flux":[], "Velocity":[], 'Fnu':[], 'Flam':[], 'Luminosity':[],'Nflux':[], 'Label':[], 'Filename':[]})
    st.session_state.data = data

# --- button to clear the dataframe ---#
def clear_data():
    print(st.session_state.data)
    st.session_state.data = pd.DataFrame({'line':[],'Line':[], 'Mdot':[],'Tmax':[],'Rin':[], 'Width':[], 'Inclination':[], 'Abundance':[], "SpectralType":[], "Int_Flux":[], "Velocity":[], 'Fnu':[], 'Flam':[], 'Luminosity':[],'Nflux':[], 'Label':[], 'Filename':[]})
    st.session_state.all_data = pd.DataFrame({'Velocity':[], 'Flam':[], 'Nflux':[], 'Label':[]})
    print(st.session_state.data)
st.button('Clear Data', on_click=clear_data, help='Clears all selected model parameters and plotted data.')


# Function to append non-form inputs into dataframe
def add_df(user_data=False):
    if user_data:
        l = lines[st.session_state.line]
    else:
        l = st.session_state.line
    row = pd.DataFrame({'line':[st.session_state.line],
            'Line':[l],
            'Mdot':[st.session_state.Mdot],
            'Tmax':[st.session_state.Tmax],
            'Rin':[st.session_state.Rin],
            'Width':[st.session_state.Width],
            'Inclination':[st.session_state.Inclination],
            'Abundance':[st.session_state.abund],
            "SpectralType":[st.session_state.spectral_type],
            "Int_Flux":[st.session_state.Int_Flux],
            "Velocity":[st.session_state.vel],
            "Fnu":[st.session_state.fnu],
            "Flam":[st.session_state.Flam],
            "Luminosity":[st.session_state.Luminosity],
            "Nflux":[st.session_state.Nflux],
            "Label":[st.session_state.label],
            "Filename":[st.session_state.filename]})
    # Check if the row already exists in the dataframe
    exists = ((st.session_state.data['line'] == st.session_state.line) &
              (st.session_state.data['Mdot'] == st.session_state.Mdot) &
              (st.session_state.data['Tmax'] == st.session_state.Tmax) &
              (st.session_state.data['Rin'] == st.session_state.Rin) &
              (st.session_state.data['Width'] == st.session_state.Width) &
              (st.session_state.data['Inclination'] == st.session_state.Inclination) &
              (st.session_state.data['Abundance'] == st.session_state.abund) &
              (st.session_state.data['SpectralType'] == st.session_state.spectral_type)).any()
    if not exists:
        st.session_state.data = pd.concat([st.session_state.data, row], ignore_index=True)




# --------- Sidebar for parameter selection ---------- #
with st.sidebar:

    st.header('Model Parameter Selection')

    line = st.selectbox('Select line', format_func=lambda x: lines[x], options=list(lines.keys()), key='line', help='Which spectral line to model.')

    Mdot = st.selectbox('Select Mdot', mdot_list, key='Mdot', help='The mass accretion rate in solar masses per year.')
    mdot_idx = np.where(mdot_list  == Mdot)


    Tmax = st.selectbox('Select Tmax', temps_list[mdots[f'M{mdot_idx[0][0]+1:02d}']['tmin']:mdots[f'M{mdot_idx[0][0]+1:02d}']['tmax']] , key='Tmax', help='The maximum temperature in Kelvin.')
    
    Rin = st.selectbox('Select Rin', np.sort(mag_ids['Rin'][~np.isnan(mag_ids['Rin'])].unique()), key='Rin', help='The inner radius of the disk in stellar radii.')

    width = st.selectbox('Select width', np.sort(mag_ids['Width'][~np.isnan(mag_ids['Width'])].unique()), key='Width', help='The width of the disk in stellar radii.')

    inc= st.selectbox('Select inclination', [15,30,45,60,75], key='Inclination', help='The inclination angle of the disk in degrees.')
    if line[0:2] == 'ca':

        # print(abundances.keys())
        if st.session_state.get('abund') is None:
            st.session_state.abund = list(abundances.keys())[0]
        abund = st.selectbox('Select Ca abundance',format_func=lambda x: abundances[x], options=list(abundances.keys()), key='abund', placeholder='Ca', help='The Calcium abundance.', )
    else:

        # abund = st.selectbox('Select Ca abundance',options=['h'], key='abund', disabled=True, placeholder='')
        abund= ""
        st.session_state.abund = ""
        # st.form_submit_button('Submit my picks')

    spectral_type = st.selectbox('Select Spectral Type', ['K2','K5','K7', 'M1','M3','M5'], key='spectral_type', help='The spectral type of the star.')
    #                     disabled=True)

    abundance = abund
    if abundance==None:
        abundance = ""
    mdot_idx = np.where(mdot_list  == Mdot)
    tmax_idx = np.where(temps_list == Tmax)[0][0]+1
    geo_idx = mag_ids[ (mag_ids['Rin'] == Rin) & (mag_ids['Width'] == width)]['ID'].values[0]
    file_name = f'prof.{line}{abundance}.G{geo_idx:02d}.M{mdot_idx[0][0]+1:02d}.T{tmax_idx:02d}.I{int(inc)}.0'

    st.session_state.filename = file_name
    
    # Load the data
    profdata = load_data(file_name,spectral_type,line)
    vel = profdata['Velocity'].data # Km/s
    fnu = profdata['Flux'].data # erg/cm^2/s/Hz at the surface of the star
    st.session_state.vel = vel
    st.session_state.fnu = fnu

    v1,v2 = vel[0], vel[-1]
    f1,f2 = fnu[0],fnu[-1]

    m = (f2-f1)/(v2-v1)
    f_cont = m * (vel-v1) + f1

    wave = (vel*(u.km/u.s)/c.to('km/s')  + 1)*(line_centers[line]*u.nm).to(u.AA)
    flb = fnu * (u.erg/u.s/u.cm**2/u.Hz) * c.to(u.AA/u.s) / ((line_centers[line]*u.nm).to(u.AA))**2 # convert from Fnu to Flam
    flb = flb.to(u.erg/u.s/u.cm**2/u.AA)

    st.session_state.Flam = flb.value


    # get radius of star based on spectral type from file
    stellar_params = pd.read_csv('https://raw.githubusercontent.com/marmicolta/database_magneto_models/refs/heads/main/model_stellar_parameters.csv')
    radius = float(stellar_params.iloc[np.where(stellar_params['SpT'] == spectral_type)[0][0]]['R'])*u.Rsun
    radius = radius.to(u.cm)

  
    flb_res = ( (fnu-f_cont) * (u.erg/u.s/u.cm**2/u.Hz) * c.to(u.AA/u.s) / (wave)**2).to(u.erg/u.s/u.cm**2/u.AA) 

    luminosity = 4*np.pi*radius**2* (flb_res)

    st.session_state.Luminosity = luminosity/L_sun.cgs # convert to Lsun
    st.session_state.Nflux = fnu/f_cont


    Int_Flux = get_flux(fnu, vel, line)
    st.session_state.Int_Flux = Int_Flux.value

    label = f"{lines[line]}|{Mdot:.2f}|{Tmax:.0f}|{Rin}|{width}|{inc:.0f}|{spectral_type}|{abundance}|{Int_Flux.value:.2e}"

    label = label.replace('.Ca',' Ca Solar').replace('_0p5',' 50% Solar').replace('_0p1',' 10% Solar').replace('_0p01',' 1% Solar')
    st.session_state.label = label

    st.button('Submit', on_click=add_df)

# -------let user upload their own models ------- #
uploaded_file = st.sidebar.file_uploader("Upload your own model data (CSV with columns: Velocity, Flux, Distance)", accept_multiple_files=False)

def add_user_file():
    success = st.toast("File uploaded successfully!", duration='short')

    # check if session state doesn't alreayd contain the user model, if not add it to the dataframe
    if not (st.session_state.data['Filename'] == uploaded_file.name).any():


        st.session_state.vel = user_data['Velocity']
        st.session_state.Flam = user_data['Flux'] #erg/s/cm^2/AA
        dist = user_data['Distance'][0]*u.pc
        dist = dist.to(u.cm)    

        vel = st.session_state.vel
        flb = st.session_state.Flam
        v1,v2 = vel[0], vel[-1]
        f1,f2 = flb[0],flb[-1]

        m = (f2-f1)/(v2-v1)
        f_cont = m * (vel-v1) + f1 

        st.session_state.Luminosity = (dist**2 * 4 * np.pi * (user_data['Flux']-f_cont))/L_sun.cgs #should be flux above the continuum!
        st.session_state.Nflux = flb/f_cont


        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame({'line':[uploaded_file.name], 'Line':[uploaded_file.name], 'Mdot':[np.nan],'Tmax':[np.nan],'Rin':[None], 'Width':[None], 'Inclination':[np.nan], 'Abundance':[""], "SpectralType":[np.nan], "Int_Flux":[np.nan], "Velocity":[user_data['Velocity']], 'Flam':[user_data['Flux']], 'Luminosity':[st.session_state.Luminosity], 'Nflux':[st.session_state.Nflux], 'Label':[uploaded_file.name], 'Filename':[uploaded_file.name]})], ignore_index=True)

# check that file has first 3 columns that are numerical
if uploaded_file is not None:
    print(uploaded_file.name)
    try:
        user_data = ascii.read(uploaded_file, names=['Velocity','Flux', 'Distance'])
        # find if all values in the first two columns are numerical, then add the file to the dataframe, otherwise show an error message
        if type(user_data['Velocity'].data.dtype) not in [np.dtypes.Float64DType, np.dtypes.Float32DType, np.dtypes.Int64DType, np.dtypes.Int32DType] or type(user_data['Flux'].data.dtype) not in [np.dtypes.Float64DType, np.dtypes.Float32DType, np.dtypes.Int64DType, np.dtypes.Int32DType] or type(user_data['Distance'].data[0]) not in [np.float64, np.float32, np.int64, np.int32]:
            st.error("CSV file must have numerical values in 'Velocity', 'Flux', and 'Distance' columns.")
        else:
             st.sidebar.button('Submit', on_click=add_user_file, key='upload_button')
    except Exception as e:
        error = st.error(f"Error reading file: {e}")



# ---- create a custom colormap for the dataframe gradients ---- #
if (st.context.theme.type == "dark"):
    
    colors= ["#000000FF","#421755FF"]
else:
    colors= ["#FFFFFFFF","#E3CDEDFF"]


custom_cmap = mcolors.LinearSegmentedColormap.from_list("my_gradient", colors, N=20)
custom_cmap_r = mcolors.LinearSegmentedColormap.from_list("my_gradient_r", colors[::-1], N=20)

# make gmap an integer mapping of the line names from 0-10
line_map = {line: i for i, line in enumerate(st.session_state.data['Line'].unique())}
abundance_map = {abundance: i for i, abundance in enumerate(st.session_state.data['Abundance'].unique()) if pd.notna(abundance)}
spectraltype_map = {spt: i for i, spt in enumerate(st.session_state.data['SpectralType'].unique())}


styled_df = st.session_state.data.style.background_gradient(cmap=custom_cmap_r, axis=0, subset=['Line'], gmap=st.session_state.data['Line'].map(line_map))#, vmin=mdot_list.min(), vmax= mdot_list.max())
styled_df = styled_df.background_gradient(cmap=custom_cmap, axis=0, subset=['Mdot'])#, vmin=mag_ids['Mdot'].min(), vmax=mag_ids['Mdot'].max())
styled_df = styled_df.background_gradient(cmap=custom_cmap, axis=0, subset=['Tmax'])#, vmin=temps_list.min(), vmax=temps_list.max())
styled_df = styled_df.background_gradient(cmap=custom_cmap, axis=0, subset=['Rin'])#, vmin=mag_ids['Rin'].min(), vmax=mag_ids['Rin'].max())
styled_df = styled_df.background_gradient(cmap=custom_cmap, axis=0, subset=['Width'])#, vmin=mag_ids['Width'].min(), vmax=mag_ids['Width'].max())
styled_df = styled_df.background_gradient(cmap=custom_cmap, axis=0, subset=['Inclination'])#, vmin=15, vmax=75)
styled_df = styled_df.background_gradient(cmap=custom_cmap, axis=0, subset=['Abundance'], gmap=st.session_state.data['Abundance'].map(abundance_map))
styled_df = styled_df.background_gradient(cmap=custom_cmap, axis=0, subset=['SpectralType'], gmap=st.session_state.data['SpectralType'].map(spectraltype_map))

# if user-added file, don't apply gradient to parameter columns
styled_df = styled_df.apply(lambda x: ['background-color: transparent' if x['line'] not in lines.keys() else '' for i in x], axis=1)

# show current dataframe with the option to select rows for plotting
event = st.dataframe(styled_df, width='stretch', on_select='rerun', selection_mode='multi-row', 
                     column_config={"Label": None, "Filename": None, "Velocity": None, "Flam": None, "Fnu": None, "Nflux": None, 'Luminosity': None,
                                    "line": None, "Int_Flux": st.column_config.NumberColumn("Integrated Flux (erg/s/cm^2)",format="%.2e"), "SpectralType": st.column_config.TextColumn("Spectral Type") ,
                                    "Mdot": st.column_config.NumberColumn("Mdot (Msun/yr)", format="%.2f"), "Tmax": st.column_config.NumberColumn("Tmax (K)", format="%.0f"), "Rin": st.column_config.NumberColumn("Rin (R*)", format="%.1f"), "Width": st.column_config.NumberColumn("Width (R*)", format="%.1f"), "Inclination": st.column_config.NumberColumn("Inclination (deg)", format="%.0f"), "Abundance": st.column_config.TextColumn("Abundance")})


# ---- options for plotting flux, normed flux, or luminosity and to hide legend ---- #
yaxis = st.pills('What do you want to plot on the y-axis?', ['Flux', "Normalized Flux", "Luminosity"], key='yaxis', help='''Select whether to plot flux, flux normalized to the continuum, or luminosity on the y-axis. \n If comparing against observations, it is recommended to plot either luminosity or normalized flux.''', default='Flux')
hide_legend = st.checkbox('Hide Legend', value=False, help='If checked, the legend will be hidden from the plot.')


# get only the selected rows from the dataframe and combine the data for those rows into one dataframe for plotting
def get_flux_data():
    rows = event.selection.rows
    filtered_df = st.session_state.data.iloc[rows]

    st.session_state.all_data = pd.DataFrame({'Velocity':[], 'Flam':[], 'Luminosity':[], 'Nflux':[], 'Label':[]})

    # for row in st.session_state.data.itertuples():
    for row in filtered_df.itertuples():
       
        vel = row.Velocity
        flb = row.Flam   
        luminosity = row.Luminosity
        pandas_data = pd.DataFrame({'Velocity':vel, 'Flam':flb, 'Luminosity':luminosity})

        pandas_data['Nflux'] = row.Nflux
        pandas_data['Int_Flux'] = row.Int_Flux
        pandas_data['Label'] = row.Label
       
        st.session_state.all_data = pd.concat([st.session_state.all_data, pandas_data], ignore_index=True)
       

get_flux_data()

if yaxis == 'Normalized Flux':
    flux_label = 'Normalized Fλ'
    flux_param = 'Nflux'
    flux_axis = alt.Axis(format=".1f")
elif yaxis == 'Luminosity':
    flux_label = r'Luminosity (erg/s)'
    flux_param = 'Luminosity'
    flux_axis = alt.Axis(format=".1e")
else:
    flux_label = r'Fλ (erg/s/cm²/Å)'
    flux_param = 'Flam'
    flux_axis = alt.Axis(format=".1e")


# --------- plotting the models ---------- #

if not st.session_state.all_data.empty:

    selection = alt.selection_point(fields=['Label'], bind='legend')
    selection_zoom = alt.selection_interval(bind='scales', empty='all')
    if hide_legend:
        legend=None
    else:
        legend=alt.Legend(title="Models", labelLimit=400, direction="vertical", orient="right", columns=1)
    chart1 = alt.Chart(st.session_state.all_data).mark_point().encode(
        x=alt.X('Velocity', title='Velocity (km/s)'),
        y=alt.Y(flux_param, axis=flux_axis, title=flux_label),
        color=alt.Color('Label:N', legend=legend, scale=alt.Scale(scheme='observable10')),
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
        y=alt.Y(flux_param, axis=flux_axis, title=flux_label),
        color=alt.Color('Label:N', scale=alt.Scale(scheme='observable10')),
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



# --------- footer ---------- #

with st.container():

    st.markdown(" [![Static Badge](https://img.shields.io/badge/github-repo-blue?logo=github&link=https%3A%2F%2Fgithub.com%2Fmarmicolta%2FAREPAS)](https://github.com/marmicolta/AREPAS) [![DOI](https://img.shields.io/badge/paper-RNASS-blue?style=plastic&label=paper&color=blue&link=https%3A%2F%2Fiopscience.iop.org%2Farticle%2F10.3847%2F2515-5172%2Fae5241)](https://iopscience.iop.org/article/10.3847/2515-5172/ae5241)  [![Static Badge](https://img.shields.io/badge/database-10.5281%2Fzenodo.18852909-blue?link=https%3A%2F%2Fdoi.org%2F10.5281%2Fzenodo.18852909)](https://zenodo.org/records/18852910)")

    st.markdown("App made with :heart: and :sparkles: (and a hearty number of consumed 🫓) by [Marbely Micolta](https://sites.google.com/umich.edu/marbelymicolta?usp=sharing) & [Katya Gozman](https://kgozman6159.github.io/) using Streamlit :streamlit:, python, Altair, and Pandas.")    

    st.markdown("If you use this app or the underlying model library in your research, please cite the [data release I paper](https://iopscience.iop.org/article/10.3847/2515-5172/ae5241)")

    st.markdown("Magnetospheric Accretion Model References: [Hartmann et al. (1994)](https://ui.adsabs.harvard.edu/abs/1994ApJ...426..669H/abstract), [Muzerolle et al. (2001)](https://ui.adsabs.harvard.edu/abs/2001ApJ...550..944M/abstract)")

    # st.markdown("The full model library is [publicly available](https://github.com/marmicolta/database_magneto_models) [![DOI](https://zenodo.org/badge/1144882498.svg)](https://doi.org/10.5281/zenodo.18852909). Generated by [Marbely Micolta](https://sites.google.com/umich.edu/marbelymicolta?usp=sharing) and [Thanawuth (Atom) Thanathibodee](https://www.frontier.phys.sc.chula.ac.th/thanawut-w). ")
    st.markdown("Other related papers:")
    # st.markdown("- Patiño et al. (2026),in review")
    st.markdown("- [Micolta et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...976..251M/abstract)")
    st.markdown("- [Micolta et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...953..177M/abstract)")
    st.markdown("- [Thanathibodee et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...944...90T/abstract)")
    st.markdown("- [Thanathibodee et al. (2020)](https://ui.adsabs.harvard.edu/abs/2020ApJ...892...81T/abstract)")
    st.markdown("- [Thanathibodee et al. (2019)](https://ui.adsabs.harvard.edu/abs/2019ApJ...884...86T/abstract)")

