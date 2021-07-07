import json
import argparse
import igraph as ig

import chart_studio.plotly as py
from plotly.offline import iplot
import plotly.graph_objs as go

parser = argparse.ArgumentParser()
parser.add_argument("title")
args = parser.parse_args()

data = []

with open("data.json") as f:
   data = json.load(f)
#print(data)

N=len(data['nodes'])


L=len(data['links'])
Edges=[(data['links'][k]['source'], data['links'][k]['target']) for k in range(L)]

G=ig.Graph(Edges, directed=False)

layt=G.layout('kk', dim=3) # plot network with the Kamada-Kawai layout algorithm


labels=[]
group=[]

for node in data['nodes']:
    labels.append(node['name'])
    group.append(node['group'])

Xn=[]
Yn=[]
Zn=[]

for k in range(N):
    Xn+=[layt[k][0]]
    Yn+=[layt[k][1]]
    Zn+=[layt[k][2]]

Xe=[]
Ye=[]
Ze=[]

for e in Edges:
    Xe+=[layt[e[0]][0],layt[e[1]][0],None]# x-coordinates of edge ends
    Ye+=[layt[e[0]][1],layt[e[1]][1],None]
    Ze+=[layt[e[0]][2],layt[e[1]][2],None]

trace1=go.Scatter3d(x=Xe, y=Ye, z=Ze, mode='lines', line=dict(color='rgb(125,125,125)', width=1),hoverinfo='none')

trace2=go.Scatter3d(x=Xn, y=Yn, z=Zn, mode='markers', name='actors',
                   marker=dict(symbol='circle', color=group, size=6, colorscale='Viridis',
                      line=dict(color='rgb(50,50,50)', width=0.5)), text=labels, hoverinfo='text')

axis=dict(showbackground=False, showline=False, zeroline=False, showgrid=False, showticklabels=False, title='')

layout = go.Layout(
         title=args.title,
         width=2200,
         height=1600,
         showlegend=False,
         scene=dict(
             xaxis=dict(axis),
             yaxis=dict(axis),
             zaxis=dict(axis),
        ))

data=[trace1, trace2]

fig=go.Figure(data=data, layout=layout)

fig.show()

#iplot(fig, filename='Les-Miserables')
