import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

def discrete_colorscale(bvals, colors):
    """
    bvals - list of values bounding intervals/ranges of interest
    colors - list of rgb or hex colorcodes for values in [bvals[k], bvals[k+1]],0<=k < len(bvals)-1
    returns the plotly  discrete colorscale
    """
    if len(bvals) != len(colors) + 1:
        raise ValueError('len(boundary values) should be equal to  len(colors)+1 while now {} {}'.format(len(bvals), len(colors)))
    bvals = sorted(bvals)
    nvals = [(v - bvals[0]) / (bvals[-1] - bvals[0]) for v in bvals]  # normalized values

    dcolorscale = []  # discrete colorscale
    for k in range(len(colors)):
        dcolorscale.extend([[nvals[k], colors[k]], [nvals[k + 1], colors[k]]])
    return dcolorscale

def fill_wafer_map(df, nrow, ncol, retmap, sort_bin, blackout_str ):
    map = np.full((nrow*retmap.shape[0], ncol*retmap.shape[1]),"__")
    #blackout = [(1,1),(1,2),(1,8),(1,9),(1,10), (2,1),(2,10),(7,1),(7,10),(8,1),(8,2),(8,8),(8,9),(8,10)]
    blackout = [eval(blackout_str)]
    df['did'] = df.Row.astype(str)+"-"+df.Column.astype(str)+"-"+df.Die
    for r in range(nrow):
        for c in range(ncol):
            if (r+1, c+1) in blackout:
                continue
            reticle = "R{}C{}".format(r+1, c+1)
            if reticle not in df.Reticle.unique():
                map[r*retmap.shape[0]:(r+1)*retmap.shape[0], c*retmap.shape[1]:(c+1)*retmap.shape[1]] = sort_bin['unbonded']
                map[(r+1)*retmap.shape[0]-1, (c+1)*retmap.shape[1]-1] = sort_bin['PCM']
            else:
                for rr in range(retmap.shape[0]):
                    for rc in range(retmap.shape[1]):
                        die = "{}-{}-{}".format(r+1, c+1, retmap[rr, rc])
                        if not df.loc[df.did == die, "PIC Grade"].empty:
                            map[r*retmap.shape[0]+rr, c*retmap.shape[1]+rc] = sort_bin[df.loc[df.did == die, "PIC Grade"].values[0]]
                        else:
                            map[r* retmap.shape[0]+rr, c * retmap.shape[1] + rc] = sort_bin['unbonded']
                        map[(r+1)*retmap.shape[0]-1, (c+1)*retmap.shape[1]-1] = sort_bin['PCM']
    return map

def create_color_map(sort_bin):
    arr = np.linspace(0,1,len(sort_bin)+1)
    sort_key = {}
    for i in arr:
        sort_key[i] = sort_bin[i]
    sort_key[1] = "@@"



def plot_wafer_map(wmap, rcid_map, sort_bin):
    colors = px.colors.qualitative.Alphabet[:len(sort_bin.keys())]
    bvals = range(len(sort_bin.keys())+1)
    print(len(colors), len(bvals))
    dcolorsc = discrete_colorscale(bvals, colors)
    sort_key = {"__":np.nan}
    print('bvals',list(bvals))

    #print(new_wmap)
    bvals = np.array(bvals)
    #tickvals = [(dcolorsc[2*k][0]+dcolorsc[2*k+1][0])/2 for k in range(len(bvals) - 1)]
    tickvals = [np.mean(bvals[k:k + 2]) for k in
                range(len(bvals) - 1)]  # position with respect to bvals where ticktext is displayed
    print(tickvals)
    ticktext = list(sort_bin.keys())
    for i, val in zip(sort_bin.keys(), bvals):
        sort_key[sort_bin[i]] = val
    sort_key[sort_bin[list(sort_bin.keys())[-1]]] = bvals[-1]
    new_wmap = np.array([[sort_key[i] for i in row ] for row in wmap])
    print(ticktext)
    print(dcolorsc)
    rcid_map = [[tx.replace("_", "") for tx in row] for row in rcid_map]

    heatmap = go.Heatmap(z=np.flipud(new_wmap), xgap=4, ygap=4,
                         colorscale=dcolorsc,
                         colorbar=dict(thickness=25,
                                       tickvals=tickvals,
                                       ticktext=ticktext),
                         hovertext = np.flipud(rcid_map))
    fig = go.Figure(data=[heatmap],)
    fig.update_layout(template="plotly_white", width=700, height=700)
    return fig


def plot_wafer_map_sns(wmap, sort_bin):
    cmap = sns.color_palette("tab10", len(sort_bin.keys()))
    bvals = range(len(sort_bin.keys()))
    sort_key = {"__":np.nan}
    for i, val in zip(sorted(sort_bin.keys())[::-1], bvals):
        sort_key[sort_bin[i]] = val
    #sort_key[sort_bin[list(sort_bin.keys())[-1]]] = bvals[-1]
    new_wmap = np.array([[sort_key[i] for i in row ] for row in wmap])
    fig, ax = plt.subplots()
    sns.heatmap(new_wmap, cmap = cmap, linewidths=.5, linecolor='white', ax = ax,xticklabels=False, yticklabels=False)
    colorbar = ax.collections[0].colorbar
    r = colorbar.vmax - colorbar.vmin
    n = len(sort_bin.keys())
    colorbar.set_ticks([colorbar.vmin + 0.5 * r / (n) + r * i / (n) for i in range(n)])
    colorbar.set_ticklabels(sorted(list(sort_bin.keys()))[::-1])
    return fig


def fill_wafer_map_rcid(nrow, ncol, retmap):
    wmap = np.full((nrow*retmap.shape[0], ncol*retmap.shape[1]),"________")
    blackout = [(1,1),(1,2),(1,8),(1,9),(1,10), (2,1),(2,10),(7,1),(7,10),(8,1),(8,2),(8,8),(8,9),(8,10)]
    for r in range(nrow):
        for c in range(ncol):
            if (r+1, c+1) in blackout:
                continue
            for rr in range(retmap.shape[0]):
                for rc in range(retmap.shape[1]):
                    wmap[r * retmap.shape[0] + rr, c * retmap.shape[1] + rc] = "R{}C{}-{}".format(r+1,c+1,retmap[rr,rc]).ljust(8,"_")
    return wmap


if __name__ == '__main__':
    raw_df = pd.read_csv(r"C:\Users\yu-sheng.kuo\Desktop\Yield, by module (Alpha2, pipecleaner only).csv")
    for wafer in raw_df.Wafer.unique().tolist():
        lot = "B47052"
        print('wafer', wafer)
        df = raw_df[raw_df.Wafer == wafer]
        print(df)
        upfront_text = """DEVICE:MSK-00280
PART#:313-00021
LOT:{}
WAFER:{}
FNLOC:180
ROWCT:40
COLCT:20
BCEQU:00
DUTMS:um
XDIES:7958
YDIES:4150
ShotMap\n""".format(lot, wafer)
        retmap = np.array([['A', 'B'], ['C', 'D'], ['E', 'F'], ['G', 'H'], ['I', 'J']])
        sort_bin = {1: 'AA', 0.5: 'BB', 0: "FF", 'unbonded': "01", 'PCM': "@@"}
        wmap = fill_wafer_map(df, 8, 10, retmap,sort_bin)
        text_file = open(r"C:\Users\yu-sheng.kuo\Desktop\{}_W{}_PnPMap.txt".format(lot, wafer), 'w')
        text_file.write(upfront_text)

        for row in wmap:
            text_file.write("RowData:")
            w = ' '.join(str(cell) for cell in row)
            text_file.write(w+'\n')
        text_file.close()
        text_file = open(r"C:\Users\yu-sheng.kuo\Desktop\{}_W{}_RCIDMap.txt".format(lot, wafer), 'w')
        text_file.write(upfront_text)
        rcidMap = fill_wafer_map_rcid(8, 10, retmap)
        for row in rcidMap:
            text_file.write("RowData:")
            w = ' '.join(str(cell) for cell in row)
            text_file.write(w+'\n')
        text_file.close()
        plot_wafer_map(wmap, rcidMap, sort_key = {"__": np.nan, "01": 0.1, "FF":0.3, "BB":0.5, "AA":0.7, "@@":0.9},)
