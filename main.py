import streamlit as st
import pandas as pd
from create_map import fill_wafer_map,plot_wafer_map, fill_wafer_map_rcid, plot_wafer_map_sns
import numpy as np

retmap = np.array([['A', 'B'], ['C', 'D'], ['E', 'F'], ['G', 'H'], ['I', 'J']])
#ret_name = ['A',"B","C","D",'E','F',"G",'H',"I","J","K","L","M","N","O","P"]
ret_name = ["D"+str(x).zfill(2) for x in range(1,100)]
sort_bin = {1: 'AA', 0.5: 'BB', 0.25:'CC',0.1:'DD', 0: "FF", 'unbonded': "01", 'PCM': "@@"}
sort_key = {"__": np.nan, "01": 0.1, "FF":0.2, "BB":0.3, "AA":0.4,'CC':0.6,'DD':0.7, "@@":0.9}
st.set_page_config(layout="wide")
erica = [(1,1),(1,2),(1,7),(1,8),(1,10), (2,1),(2,8),(6,1),(6,8),(7,1),(7,2),(7,7),(7,8)]

def create_sinf(wafermap, lot, wafer):
    wmap_txt = "DEVICE:MSK-00280\nPART#:313-00021\nLOT:{}\nWAFER:{}\nFNLOC:180\nROWCT:40\nCOLCT:20\nBCEQU:00\nDUTMS:um\nXDIES:7958\nYDIES:4150\nShotMap\n".format(lot, wafer)
    for row in wafermap:
        wmap_txt += "RowData:"
        w = ' '.join(str(cell) for cell in row)
        wmap_txt += (w + '\n')
    return wmap_txt


def create_rcid(rcidmap, lot, wafer):
    wmap_txt = "DEVICE:MSK-00280\nPart#:313-00021\nLOT:{}\nWAFER:{}\nFNLOC:180\nROWCT:40\nCOLCT:20\nBCEQU:00\nDUTMS:um\nXDIES:7958\nYDIES:4150\nShotMap\n".format(lot, wafer)
    for row in rcidmap:
        wmap_txt += "RowData:"
        w = ' '.join(str(cell) for cell in row)
        wmap_txt += (w + '\n')
    return wmap_txt

# Add a selectbox to the sidebar:
uploaded_file = st.sidebar.file_uploader(
    'Upload yield file(*.csv)',
)


if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    yield_df = pd.read_csv(uploaded_file)
    bin_category = yield_df['PIC Grade'].unique().tolist()
    sort_bin = {'unbonded': "01", 'PCM': "@@"}
    for i in bin_category:
        sort_bin[i] = "{}{}".format(i, i)


    # Add Wafer select
    lot = st.sidebar.text_input("LOT",placeholder = "L000000")
    wafer_select = ""
    if yield_df.Wafer.unique().tolist():
        wafer_select = st.sidebar.selectbox('Select Wafer', yield_df.Wafer.unique())
    # Add Row number
    ReticleRow = st.sidebar.number_input('Reticle Row Number:', value = 8, format='%i')
    ReticleCol = st.sidebar.number_input("Reticle Col Number:", value = 10, format='%i')
    dieRow = st.sidebar.number_input('Die Row number:', value = 5, format = '%i')
    dieCol = st.sidebar.number_input('Die Col number:', value = 2, format = '%i')
    PCM_row = st.sidebar.number_input('PCM Row loc', value = 5)
    PCM_col = st.sidebar.number_input('PCM Col loc', value = 2)
    blackout_str = st.sidebar.text_area('Black out reticle', value =
    "(1,1),(1,2),(1,8),(1,9),(1,10), (2,1),(2,10),(7,1),(7,10),(8,1),(8,2),(8,8),(8,9),(8,10)")
    # Add sort rule

    # rule = st.sidebar.text_input('Sort Rule', placeholder='Write sort rule based on python logic, seperated by newline("\n")')

    clicked = st.sidebar.button(label="Plot", )

    if clicked is not None:
        st.header("Wafer Map")
        st.subheader('LOT:{} Wafer:{}'.format(lot, wafer_select))
        #st.subheader('Sort Group:{}'.format(list(sort_bin.keys())))
        retmap = np.array(ret_name[:dieRow*dieCol]).reshape((dieRow, dieCol))
        print(retmap)
        wmap = fill_wafer_map(yield_df[yield_df.Wafer == int(wafer_select)], ReticleRow, ReticleCol, retmap, sort_bin, blackout_str ,PCM_row,PCM_col)
        rcid_map = fill_wafer_map_rcid(ReticleRow, ReticleCol, retmap)
        #wmap_fig = plot_wafer_map(wmap,rcid_map, sort_bin)
        #st.write(wmap_fig)
        wmap_fig = plot_wafer_map_sns(wmap, sort_bin)
        st.write(wmap_fig)
        wmap_txt = create_sinf(wmap, lot, wafer_select, )
        rcid_txt = create_rcid(rcid_map,lot, wafer_select,)
        st.download_button(
             label="Download SINF file",
             data=wmap_txt,
             file_name='PnP_{}_{}.txt'.format(lot, wafer_select),
             mime='text/csv',
         )
        st.download_button(
            label="Download RCID file",
            data=rcid_txt,
            file_name='RCID_{}_{}.txt'.format(lot, wafer_select),
            mime='text/csv',
        )





