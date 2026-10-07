import math
import plotly.graph_objects as go

MODULE_COLORS = {
    "Funding Ecosystem":"#6F42C1",
    "Collaboration Structure":"#F28C28",
    "Geographic Diversification":"#8E63D2",
    "Institutional Position":"#FFB15A",
    "Temporal Resilience":"#5B2E91",
    "Strategic Internationalization":"#D97706",
}

CONSTRUCTS={
    "Funding Ecosystem":["External Funding","Funding Concentration","Funding Efficiency"],
    "Collaboration Structure":["International Network","Partner Portfolio","Consortium Architecture"],
    "Geographic Diversification":["Country Diversity","Cross-Regional Reach","Funding Geography"],
    "Institutional Position":["Centrality","Coordination Role","Portfolio Scale"],
    "Temporal Resilience":["Persistence","Continuity","Longitudinal Stability"],
    "Strategic Internationalization":["Resilient Partnerships","Funding Capacity","Strategic Positioning"],
}

INDICATORS={
    "External Funding":["EC contribution","Project portfolio"],
    "Funding Concentration":["Funding Gini","Collaboration HHI"],
    "Funding Efficiency":["Funding per project","Funding per participation"],
    "International Network":["Degree","Betweenness","PageRank"],
    "Partner Portfolio":["Partner count","Diversification 1-HHI"],
    "Consortium Architecture":["Organisations per project","Countries per project"],
    "Country Diversity":["Countries connected","Network community"],
    "Cross-Regional Reach":["Bilateral links","Collaboration weight"],
    "Funding Geography":["Funding by country","Programme portfolio"],
    "Centrality":["Degree centrality","Eigenvector","PageRank"],
    "Coordination Role":["Coordinator share","Coordinator portfolio"],
    "Portfolio Scale":["Projects","Participations","Organisations"],
    "Persistence":["Active collaboration years","Mean persistence"],
    "Continuity":["Repeated links","Maximum persistence"],
    "Longitudinal Stability":["Annual projects","Annual funding"],
    "Resilient Partnerships":["Diversity × persistence","Community structure"],
    "Funding Capacity":["External funding","Funding per project"],
    "Strategic Positioning":["Centrality × funding","Coordination × diversity"],
}

MODULE_ES={
    "Funding Ecosystem":"Ecosistema de financiación",
    "Collaboration Structure":"Estructura de colaboración",
    "Geographic Diversification":"Diversificación geográfica",
    "Institutional Position":"Posición institucional",
    "Temporal Resilience":"Resiliencia temporal",
    "Strategic Internationalization":"Internacionalización estratégica",
}

def _pt(r,a):
    return r*math.cos(a), r*math.sin(a)

def _wrap(label):
    words=label.split()
    if len(words)<=2:
        return "<br>".join(words)
    mid=(len(words)+1)//2
    return " ".join(words[:mid])+"<br>"+" ".join(words[mid:])

def _anchor(x,y):
    if abs(x)>abs(y):
        return ("left" if x>=0 else "right"), "middle"
    return "center", ("bottom" if y>=0 else "top")

def ontology_figure(lang="EN"):
    es=lang=="ES"
    root=("Colaboración Universitaria<br>Internacional Resiliente" if es else
          "Resilient International<br>University Collaboration")
    modules=list(CONSTRUCTS.keys())
    edge_x=[];edge_y=[];module_pts=[];construct_pts=[];indicator_pts=[]
    module_angles={m:(math.pi/2-i*2*math.pi/len(modules)) for i,m in enumerate(modules)}
    for mod in modules:
        a=module_angles[mod];mx,my=_pt(1.55,a);module_pts.append((mod,mx,my));edge_x += [0,mx,None];edge_y += [0,my,None]
        for con,off in zip(CONSTRUCTS[mod],[-0.30,0,0.30]):
            ca=a+off;cx,cy=_pt(2.55,ca);construct_pts.append((mod,con,cx,cy));edge_x += [mx,cx,None];edge_y += [my,cy,None]
            inds=INDICATORS.get(con,[]);ioffs=[0] if len(inds)==1 else ([-0.09,0.09] if len(inds)==2 else [-0.12,0,0.12])
            for ind,ioff in zip(inds,ioffs):
                ix,iy=_pt(3.35,ca+ioff);indicator_pts.append((mod,ind,ix,iy));edge_x += [cx,ix,None];edge_y += [cy,iy,None]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=edge_x,y=edge_y,mode="lines",line=dict(width=.85,color="#C8D4DE"),hoverinfo="none",showlegend=False))
    fig.add_trace(go.Scatter(x=[0],y=[0],mode="markers",marker=dict(size=50,color="#17324D",line=dict(width=1.2,color="white")),hovertext=[root.replace("<br>"," ")],hoverinfo="text",showlegend=False))
    fig.add_annotation(x=0,y=.08,text=root,showarrow=False,xanchor="center",yanchor="bottom",font=dict(family="Times New Roman",size=13,color="#17324D"),align="center")
    for mod,mx,my in module_pts:
        label=MODULE_ES.get(mod,mod) if es else mod;fig.add_trace(go.Scatter(x=[mx],y=[my],mode="markers",marker=dict(size=34,color=MODULE_COLORS[mod],line=dict(width=1.2,color="white")),hovertext=[label],hoverinfo="text",showlegend=False))
        xa,ya=_anchor(mx,my);fig.add_annotation(x=mx,y=my,text=_wrap(label),showarrow=False,xanchor=xa,yanchor=ya,font=dict(family="Times New Roman",size=13,color="#17324D"),align="center",xshift=10 if xa=="left" else (-10 if xa=="right" else 0),yshift=10 if ya=="bottom" else (-10 if ya=="top" else 0))
    for mod,con,cx,cy in construct_pts:
        fig.add_trace(go.Scatter(x=[cx],y=[cy],mode="markers",marker=dict(size=20,color=MODULE_COLORS[mod],line=dict(width=1,color="white")),hovertext=[con],hoverinfo="text",showlegend=False))
        xa,ya=_anchor(cx,cy);fig.add_annotation(x=cx,y=cy,text=_wrap(con),showarrow=False,xanchor=xa,yanchor=ya,font=dict(family="Times New Roman",size=13,color="#17324D"),align="center",xshift=9 if xa=="left" else (-9 if xa=="right" else 0),yshift=9 if ya=="bottom" else (-9 if ya=="top" else 0))
    for mod,ind,ix,iy in indicator_pts:
        fig.add_trace(go.Scatter(x=[ix],y=[iy],mode="markers",marker=dict(size=7,color=MODULE_COLORS[mod],line=dict(width=.6,color="white")),hovertext=[ind],hoverinfo="text",showlegend=False))
    for name,color,size in [("Core","#17324D",14),("Modules","#6F42C1",12),("Constructs","#F28C28",9),("Indicators","#8E63D2",6)]:
        fig.add_trace(go.Scatter(x=[None],y=[None],mode="markers",name=name,marker=dict(size=size,color=color),showlegend=True))
    fig.update_layout(title=None,height=930,paper_bgcolor="white",plot_bgcolor="white",xaxis=dict(visible=False,range=[-4.05,4.05]),yaxis=dict(visible=False,range=[-3.9,3.9],scaleanchor="x",scaleratio=1),margin=dict(l=35,r=35,t=30,b=95),font=dict(family="Times New Roman",size=13,color="#17324D"),legend=dict(orientation="h",y=-.025,x=.5,xanchor="center",font=dict(size=13)))
    return fig
