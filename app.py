
import io, csv, re, zipfile
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import pycountry

from analytics import (
    build_edges,country_year_table,country_metrics,gini,spearman_matrix,spearman_fdr,
    pca_analysis,cluster_analysis,annual_growth,consortium_sizes,pair_persistence
)
from ontology import ontology_figure

APP_VERSION="1.0.0"
BASE=Path(__file__).resolve().parent
SEED_FILE=BASE/"cordis_real_seed.csv"

URLS={
"HORIZON":"https://cordis.europa.eu/data/cordis-HORIZONprojects-csv.zip",
"H2020":"https://cordis.europa.eu/data/cordis-h2020projects-csv.zip",
}

PALETTE=["#6F42C1","#F28C28","#8E63D2","#FFB15A","#5B2E91","#D97706","#B084F5","#F4A261","#7C3AED"]


COUNTRY_NAME_OVERRIDES = {
    "XK": "Kosovo",
    "TW": "Taiwan",
    "PS": "Palestine",
    "TR": "Türkiye",
    "BO": "Bolivia",
    "VE": "Venezuela",
    "MD": "Moldova",
    "TZ": "Tanzania",
    "RU": "Russia",
    "IR": "Iran",
    "SY": "Syria",
    "LA": "Laos",
    "VN": "Vietnam",
    "KR": "South Korea",
    "KP": "North Korea",
    "CZ": "Czechia",
    "CI": "Côte d’Ivoire",
    "CV": "Cabo Verde",
    "SZ": "Eswatini",
}

def country_name_from_code(code):
    c = str(code).strip().upper()
    if not c or c == "NAN":
        return c
    if c in COUNTRY_NAME_OVERRIDES:
        return COUNTRY_NAME_OVERRIDES[c]
    try:
        return pycountry.countries.get(alpha_2=c).name
    except Exception:
        return c

def country_label(code):
    return country_name_from_code(code)

REGION_PRESETS = {
    "Latin America": [
        "AR","BO","BR","CL","CO","CR","CU","DO","EC","SV","GT","HN",
        "MX","NI","PA","PY","PE","PR","UY","VE"
    ],
    "Hispanic America": [
        "AR","BO","CL","CO","CR","CU","DO","EC","SV","GT","HN",
        "MX","NI","PA","PY","PE","PR","UY","VE"
    ],
    "Europe": [
        "AD","AL","AT","BA","BE","BG","BY","CH","CY","CZ","DE","DK","EE","ES",
        "FI","FR","GB","GR","HR","HU","IE","IS","IT","LI","LT","LU","LV","MC",
        "MD","ME","MK","MT","NL","NO","PL","PT","RO","RS","RU","SE","SI","SK",
        "SM","UA","VA","XK"
    ],
    "Asia": [
        "AE","AF","AM","AZ","BD","BH","BN","BT","CN","GE","HK","ID","IL","IN",
        "IQ","IR","JO","JP","KG","KH","KP","KR","KW","KZ","LA","LB","LK","MM",
        "MN","MO","MV","MY","NP","OM","PH","PK","PS","QA","SA","SG","SY","TH",
        "TJ","TL","TM","TR","TW","UZ","VN","YE"
    ],
    "Africa": [
        "AO","BF","BI","BJ","BW","CD","CF","CG","CI","CM","CV","DJ","DZ","EG",
        "ER","ET","GA","GH","GM","GN","GQ","GW","KE","KM","LR","LS","LY","MA",
        "MG","ML","MR","MU","MW","MZ","NA","NE","NG","RW","SC","SD","SL","SN",
        "SO","SS","ST","SZ","TD","TG","TN","TZ","UG","ZA","ZM","ZW"
    ],
    "North America": [
        "CA","US","MX","GT","BZ","HN","SV","NI","CR","PA","CU","DO","HT","JM",
        "BS","BB","TT","GD","LC","VC","AG","KN","DM"
    ],
    "Oceania": [
        "AU","NZ","FJ","PG","SB","VU","WS","TO","TV","KI","NR","PW","FM","MH"
    ],
    "Middle East": [
        "AE","BH","IL","IQ","IR","JO","KW","LB","OM","PS","QA","SA","SY","TR","YE"
    ],
    "European Union": [
        "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE",
        "IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"
    ],
    "Ibero-America": [
        "AR","BO","BR","CL","CO","CR","CU","DO","EC","SV","GT","HN","MX","NI",
        "PA","PY","PE","PR","UY","VE","ES","PT"
    ],
}

REGION_LABEL_ES = {
    "Latin America": "Latinoamérica",
    "Hispanic America": "Hispanoamérica",
    "Europe": "Europa",
    "Asia": "Asia",
    "Africa": "África",
    "North America": "Norteamérica",
    "Oceania": "Oceanía",
    "Middle East": "Medio Oriente",
    "European Union": "Unión Europea",
    "Ibero-America": "Iberoamérica",
}

st.set_page_config(page_title="Research Partnership Atlas v1.0.0",page_icon="🌍",layout="wide")

# ---- Startup guard ----
if "REGION_PRESETS" not in globals():
    raise RuntimeError("Research Partnership Atlas installation error: REGION_PRESETS is missing. Re-extract the complete release into a new folder.")


def norm(s): return re.sub(r"[^a-z0-9]","",str(s).lower())

def find_col(df,candidates):
    cmap={norm(c):c for c in df.columns}
    for c in candidates:
        if norm(c) in cmap:return cmap[norm(c)]
    for col in df.columns:
        n=norm(col)
        if any(norm(c) in n or n in norm(c) for c in candidates):return col
    return None

def parse_csv(raw):
    text=None
    for enc in ("utf-8-sig","utf-8","latin-1"):
        try:text=raw.decode(enc);break
        except UnicodeDecodeError:pass
    if text is None:raise ValueError("Could not decode CSV")
    sample=text[:30000]
    try: delimiter=csv.Sniffer().sniff(sample,delimiters=";,\t").delimiter
    except Exception:
        first=text.splitlines()[0] if text.splitlines() else ""
        delimiter=";" if first.count(";")>=first.count(",") else ","
    reader=csv.reader(io.StringIO(text),delimiter=delimiter,quotechar='"',doublequote=True)
    header=next(reader); header=[x.strip().lstrip("\ufeff") for x in header]; w=len(header)
    rows=[]
    for row in reader:
        if not row:continue
        if len(row)<w:row=row+[""]*(w-len(row))
        if len(row)>w:row=row[:w]
        rows.append(row)
    return pd.DataFrame(rows,columns=header)

@st.cache_data(ttl=21600,show_spinner=False)
def fetch_programme(prog):
    r=requests.get(URLS[prog],headers={"User-Agent":f"Mozilla/5.0 Research Partnership Atlas/{APP_VERSION} academic research"},timeout=300)
    r.raise_for_status()
    z=zipfile.ZipFile(io.BytesIO(r.content))
    names=z.namelist()
    p=[n for n in names if Path(n).name.lower()=="project.csv"]
    o=[n for n in names if Path(n).name.lower() in ("organization.csv","organisation.csv")]
    if not p:p=[n for n in names if "project" in Path(n).name.lower() and n.endswith(".csv")]
    if not o:o=[n for n in names if "organi" in Path(n).name.lower() and n.endswith(".csv")]
    if not p or not o:raise RuntimeError("project.csv or organization.csv not found in official CORDIS ZIP")
    return parse_csv(z.read(p[0])),parse_csv(z.read(o[0]))

def canonical_projects(df,prog):
    def s(cands):
        c=find_col(df,cands);return df[c] if c else pd.Series([np.nan]*len(df))
    out=pd.DataFrame({
        "project_id":s(["id","projectID","projectId"]),
        "acronym":s(["acronym"]),
        "project_title":s(["title"]),
        "start_date":s(["startDate"]),
        "end_date":s(["endDate"]),
        "total_cost":pd.to_numeric(s(["totalCost"]),errors="coerce"),
        "ec_max_contribution":pd.to_numeric(s(["ecMaxContribution"]),errors="coerce"),
        "funding_scheme":s(["fundingScheme"]),
        "topic":s(["topics","topic"]),
        "grant_doi":s(["grantDoi","doi"]),
        "status":s(["status"]),
    })
    out["framework_programme"]=prog
    out["start_date"]=pd.to_datetime(out["start_date"],errors="coerce")
    out["end_date"]=pd.to_datetime(out["end_date"],errors="coerce")
    out["start_year"]=out["start_date"].dt.year
    out["source_system"]="CORDIS";out["record_status"]="OBSERVED"
    return out

COUNTRY_ALIASES = {"UK":"GB","EL":"GR"}

def sanitize_country_code(value):
    raw=str(value).strip().upper()
    raw=COUNTRY_ALIASES.get(raw,raw)
    if len(raw)!=2 or ";" in raw or "," in raw:
        return np.nan
    try:
        return raw if pycountry.countries.get(alpha_2=raw) is not None or raw=="XK" else np.nan
    except Exception:
        return np.nan

def canonical_orgs(df,prog):
    def s(cands):
        c=find_col(df,cands);return df[c] if c else pd.Series([np.nan]*len(df))
    raw_country=s(["country","countryCode"])
    out=pd.DataFrame({
        "project_id":s(["projectID","projectId"]),
        "organisation_id":s(["organisationID","organizationID"]),
        "organisation_name":s(["name","organisationName","organizationName","legalName"]),
        "raw_country":raw_country,
        "country":raw_country.map(sanitize_country_code),
        "role":s(["role"]),
        "ec_contribution":pd.to_numeric(s(["ecContribution","netEcContribution"]),errors="coerce"),
        "organisation_type":s(["activityType","organisationType","organizationType"]),
    })
    out["country_valid"]=out["country"].notna()
    out["framework_programme"]=prog
    out["source_system"]="CORDIS";out["record_status"]="OBSERVED"
    return out

def full_data(programmes):
    ps=[];os_=[];audit=[]
    for prog in programmes:
        p,o=fetch_programme(prog)
        cp,co=canonical_projects(p,prog),canonical_orgs(o,prog)
        ps.append(cp);os_.append(co)
        audit.append({"programme":prog,"projects":len(cp),"participations":len(co),
                      "source_url":URLS[prog],"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
                      "status":"OBSERVED_OFFICIAL_CORDIS"})
    return pd.concat(ps,ignore_index=True),pd.concat(os_,ignore_index=True),pd.DataFrame(audit)

def style(fig,legend=True,height=570):
    fig.update_layout(title=None,height=height,paper_bgcolor="white",plot_bgcolor="white",
        font=dict(family="Times New Roman",size=13,color="#17324D"),
        margin=dict(l=75,r=45,t=18,b=88),showlegend=legend,
        legend=dict(orientation="h",y=-.18,x=.5,xanchor="center",font=dict(size=13)))
    fig.update_xaxes(showgrid=False,zeroline=False,linecolor="#D8E3ED",automargin=True,
                     title_font=dict(size=13,family="Times New Roman"),tickfont=dict(size=13,family="Times New Roman"))
    fig.update_yaxes(gridcolor="#EAF0F5",zeroline=False,linecolor="#D8E3ED",automargin=True,
                     title_font=dict(size=13,family="Times New Roman"),tickfont=dict(size=13,family="Times New Roman"))
    return fig

def export_one_pdf_bytes(fig):
    f=go.Figure(fig)
    f.update_layout(title=None,font=dict(family="Times New Roman",size=13,color="#17324D"))
    return f.to_image(format="pdf")

def export(fig,stem,key):
    try:
        pdf=export_one_pdf_bytes(fig)
        st.download_button("PDF",pdf,file_name=stem+".pdf",mime="application/pdf",key=key+"p")
    except Exception:
        st.caption("PDF export requires Kaleido; installed via requirements.txt.")

def _highlight_codes(q, metric="ec_funding", n=14):
    if q.empty:return []
    codes=list(q.sort_values(metric,ascending=False).head(n)["country"])
    return list(dict.fromkeys(codes))

def scatter_country(cm,x,y,size,color,xlab,ylab,log_y=False,label_n=14):
    q=cm.replace([np.inf,-np.inf],np.nan).dropna(subset=[x,y]).copy()
    if q.empty:return go.Figure()
    q["country_name"]=q["country"].apply(country_name_from_code)
    labels=set(_highlight_codes(q,"ec_funding" if "ec_funding" in q else x,label_n))
    q["label"]=q["country"].where(q["country"].isin(labels),"")
    ss=np.clip(pd.to_numeric(q[size],errors="coerce").fillna(1),1,None)
    fig=px.scatter(q,x=x,y=y,size=ss,color=color,text="label",custom_data=["country_name","country"],
                   color_continuous_scale=[[0,"#5B2E91"],[0.5,"#B084F5"],[1,"#F28C28"]],size_max=42)
    fig.update_traces(textposition="top center",marker=dict(line=dict(width=.8,color="white"),opacity=.86),
        hovertemplate="%{customdata[0]} (%{customdata[1]})<br>x=%{x}<br>y=%{y}<extra></extra>")
    fig.update_xaxes(title=xlab);fig.update_yaxes(title=ylab,type="log" if log_y else None)
    return style(fig,False,610)

def build_figures(projects, orgs, annual, cm, G, cons, pairs, cy, pca_scores, pca_load, pca_note, clusters, cluster_note, lang="EN"):
    ES=lang=="ES"
    figs=[]

    # 1 Complete-year temporal trajectory only
    fig=go.Figure()
    if not annual.empty:
        aa=annual.sort_values("start_year").copy()
        pidx=100*aa.projects/aa.projects.max()
        fidx=100*aa.ec_funding/aa.ec_funding.max() if aa.ec_funding.max()>0 else aa.ec_funding
        fig.add_trace(go.Scatter(x=aa.start_year,y=pidx,mode="lines+markers",name="Projects index",line=dict(width=3,color=PALETTE[0]),marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=aa.start_year,y=fidx,mode="lines+markers",name="Funding index",line=dict(width=3,color=PALETTE[1]),marker=dict(size=6)))
    fig.update_xaxes(title="Año" if ES else "Year",dtick=2)
    fig.update_yaxes(title="Índice normalizado (0–100)" if ES else "Normalized index (0–100)",range=[0,105])
    figs.append(("fig01_temporal_trajectory",style(fig,True,560),"1. Trayectoria temporal en años completos" if ES else "1. Complete-year temporal trajectory"))

    # 2 Selectively labelled country positioning
    q=cm.replace([np.inf,-np.inf],np.nan).dropna(subset=["projects","ec_funding","partner_count","diversification"]).copy()
    q=q[q["ec_funding"]>0]
    q["funding_billion"]=q["ec_funding"]/1e9
    fig=scatter_country(q,"projects","funding_billion","partner_count","diversification",
                        "Proyectos" if ES else "Projects","Financiación EC (EUR billion)" if ES else "EC funding (EUR billion)",label_n=10)
    figs.append(("fig02_country_positioning",fig,"2. Posicionamiento de la cartera internacional" if ES else "2. International portfolio positioning"))

    # 3 Resilience map: density + strict selective labels
    q=cm.replace([np.inf,-np.inf],np.nan).dropna(subset=["diversification","mean_persistence","ec_funding","pagerank"]).copy()
    fig=go.Figure()
    if not q.empty:
        contour=px.density_contour(q,x="diversification",y="mean_persistence",nbinsx=20,nbinsy=16)
        for tr in contour.data:
            tr.update(contours_coloring="none",line=dict(color="#D9E1E8",width=1),hoverinfo="skip",showlegend=False)
            fig.add_trace(tr)
        fig.add_trace(go.Scatter(x=q.diversification,y=q.mean_persistence,mode="markers",marker=dict(size=6,color="#B9C3CC",opacity=.34),hoverinfo="skip",showlegend=False))
        hc=list(q.sort_values("ec_funding",ascending=False).head(5).country)
        hc+=list(q.sort_values("diversification",ascending=True).head(3).country)
        hc+=list(q.sort_values("mean_persistence",ascending=True).head(2).country)
        hc=list(dict.fromkeys(hc))
        h=q[q.country.isin(hc)].copy();h["country_name"]=h.country.apply(country_name_from_code)
        positions=["top center","bottom center","middle right","middle left"]
        textpos=[positions[i%len(positions)] for i in range(len(h))]
        fig.add_trace(go.Scatter(x=h.diversification,y=h.mean_persistence,mode="markers+text",text=h.country,textposition=textpos,
            marker=dict(size=13,color=h.pagerank,colorscale=[[0,"#5B2E91"],[.5,"#B084F5"],[1,"#F28C28"]],showscale=True,colorbar=dict(title="PageRank",len=.55,thickness=12),line=dict(width=1,color="white")),
            customdata=np.stack([h.country_name,h.ec_funding],axis=1),hovertemplate="%{customdata[0]}<br>Diversification=%{x:.3f}<br>Persistence=%{y:.2f} years<br>EC funding=%{customdata[1]:,.0f}<extra></extra>",showlegend=False,
            textfont=dict(size=13,family="Times New Roman",color="#17324D")))
        fig.add_vline(x=q.diversification.median(),line_dash="dot",line_color="#7A8793")
        fig.add_hline(y=q.mean_persistence.median(),line_dash="dot",line_color="#7A8793")
    fig.update_xaxes(title="Diversificación (1-HHI)" if ES else "Diversification (1-HHI)")
    fig.update_yaxes(title="Persistencia media (años)" if ES else "Mean persistence (years)")
    figs.append(("fig03_resilience_quadrant",style(fig,False,640),"3. Mapa estratégico de resiliencia" if ES else "3. Strategic resilience map"))

    # 4 Community-ordered matrix; top 36 valid countries only
    fig=go.Figure()
    if G.number_of_nodes() and not cm.empty:
        od=cm.dropna(subset=["country","community","pagerank"]).sort_values(["community","pagerank"],ascending=[True,False]).copy()
        selected=[]
        for _,grp in od.groupby("community",sort=True):selected.extend(grp.head(10).country.tolist())
        for code in od.country.tolist():
            if code not in selected:selected.append(code)
            if len(selected)>=36:break
        selected=selected[:36]
        sub=od[od.country.isin(selected)].sort_values(["community","pagerank"],ascending=[True,False]);selected=sub.country.tolist()
        A=nx.to_numpy_array(G,nodelist=selected,weight="weight");Z=np.log1p(A)
        names=[country_name_from_code(c) for c in selected]
        custom=[[f"{names[i]} ↔ {names[j]}<br>Shared projects={A[i,j]:.0f}" for j in range(len(selected))] for i in range(len(selected))]
        fig.add_trace(go.Heatmap(z=Z,x=selected,y=selected,colorscale=[[0,"#F7F4FB"],[.35,"#B084F5"],[.7,"#7C3AED"],[1,"#F28C28"]],zmin=0,
            colorbar=dict(title="log(1+w)",len=.55,thickness=12),customdata=custom,hovertemplate="%{customdata}<extra></extra>"))
        fig.update_yaxes(autorange="reversed")
        comm=sub.community.tolist();bounds=[]
        for i in range(1,len(comm)):
            if comm[i]!=comm[i-1]:bounds.append(i-.5)
        for b in bounds:
            fig.add_shape(type="line",x0=b,x1=b,y0=-.5,y1=len(selected)-.5,line=dict(color="white",width=2))
            fig.add_shape(type="line",x0=-.5,x1=len(selected)-.5,y0=b,y1=b,line=dict(color="white",width=2))
    fig.update_xaxes(title="Países ordenados por comunidad" if ES else "Countries ordered by community",tickangle=-90)
    fig.update_yaxes(title="Países ordenados por comunidad" if ES else "Countries ordered by community")
    figs.append(("fig04_network_communities",style(fig,False,820),"4. Estructura modular de colaboración" if ES else "4. Modular collaboration structure"))

    # 5 Lorenz/Gini
    q=cm.dropna(subset=["ec_funding"]).query("ec_funding >= 0").sort_values("ec_funding").copy()
    fig=go.Figure()
    if not q.empty and q.ec_funding.sum()>0:
        q["cum_country"]=np.arange(1,len(q)+1)/len(q);q["cum_funding"]=q.ec_funding.cumsum()/q.ec_funding.sum()
        gg=gini(q.ec_funding)
        fig.add_trace(go.Scatter(x=[0]+q.cum_country.tolist(),y=[0]+q.cum_funding.tolist(),mode="lines",name=f"Gini={gg:.3f}",line=dict(width=3,color=PALETTE[1])))
        fig.add_trace(go.Scatter(x=[0,1],y=[0,1],mode="lines",name="Equality",line=dict(dash="dot",width=2,color="#667784")))
    fig.update_xaxes(tickformat=".0%",title="Países acumulados" if ES else "Cumulative countries")
    fig.update_yaxes(tickformat=".0%",title="Financiación acumulada" if ES else "Cumulative funding")
    figs.append(("fig05_funding_lorenz",style(fig,True,560),"5. Concentración internacional de la financiación" if ES else "5. International funding concentration"))

    # 6 Consortium ECDF with square-root x scale and empirical quantiles
    vals=cons.organisations.dropna().astype(float)
    vals=vals[vals>0]
    fig=go.Figure()
    if len(vals):
        raw=np.sort(vals.values); x=np.sqrt(raw); y=np.arange(1,len(raw)+1)/len(raw)
        fig.add_trace(go.Scatter(x=x,y=y,mode="lines",line=dict(width=3,color=PALETTE[0]),name="ECDF"))
        for qv,dash in [(0.5,"dot"),(0.9,"dash"),(0.95,"dashdot")]:
            v=float(vals.quantile(qv)); xv=np.sqrt(v)
            fig.add_vline(x=xv,line_dash=dash,line_color="#7A8793")
            fig.add_annotation(x=xv,y=qv,text=f"P{int(qv*100)}={v:.0f}",showarrow=False,yshift=12,font=dict(size=13,family="Times New Roman"))
        vmax=float(vals.max())
        base_ticks=[1,2,5,10,20,50,100,200,500]
        ticks=[v for v in base_ticks if v<=max(vmax,1)]
        if vmax not in ticks and vmax>0: ticks.append(vmax)
        ticks=sorted(set(ticks))
        fig.update_xaxes(tickmode="array",tickvals=[np.sqrt(v) for v in ticks],ticktext=[f"{v:g}" for v in ticks])
    fig.update_xaxes(title="Organizaciones por proyecto (escala raíz cuadrada)" if ES else "Organisations per project (square-root scale)")
    fig.update_yaxes(title="Distribución acumulada" if ES else "Cumulative distribution",tickformat=".0%",range=[0,1.02])
    figs.append(("fig06_consortium_ecdf",style(fig,False,560),"6. Distribución del tamaño de consorcios" if ES else "6. Consortium-size distribution"))

    # 7 Coordination efficiency, log funding, selective labels + Spearman
    q=cm.replace([np.inf,-np.inf],np.nan).dropna(subset=["coordination_share","funding_per_project","projects","degree"]).copy();q=q[q.funding_per_project>0]
    fig=scatter_country(q,"coordination_share","funding_per_project","projects","degree",
                        "Participación como coordinador (%)" if ES else "Coordinator share (%)",
                        "Financiación por proyecto (EUR, log)" if ES else "Funding per project (EUR, log)",log_y=True,label_n=14)
    try:
        from scipy.stats import spearmanr
        r,p=spearmanr(q.coordination_share,q.funding_per_project,nan_policy="omit")
        fig.add_annotation(x=.02,y=.98,xref="paper",yref="paper",text=f"Spearman ρ={r:.2f}, p={p:.2g}",showarrow=False,align="left",font=dict(size=13))
    except Exception:pass
    figs.append(("fig07_coordination_efficiency",fig,"7. Coordinación y eficiencia de captación" if ES else "7. Coordination and funding efficiency"))

    # 8 Spearman lower-triangle with FDR; reduced to non-redundant metrics
    cols=["projects","ec_funding","funding_per_project","coordination_share","pagerank","diversification","mean_persistence"]
    rho,qvals=spearman_fdr(cm,cols,min_n=8)
    labels={"projects":"Projects","ec_funding":"EC funding","funding_per_project":"Funding/project","coordination_share":"Coordination","pagerank":"PageRank","diversification":"Diversification","mean_persistence":"Persistence"}
    z=rho.values.copy();text=np.empty(z.shape,dtype=object)
    for i in range(len(cols)):
        for j in range(len(cols)):
            if j>i or np.isnan(z[i,j]):z[i,j]=np.nan;text[i,j]=""
            else:
                qv=qvals.iloc[i,j];star="**" if pd.notna(qv) and qv<.01 else ("*" if pd.notna(qv) and qv<.05 else "")
                text[i,j]=f"{rho.iloc[i,j]:.2f}{star}"
    labs=[labels[c] for c in cols]
    fig=go.Figure(go.Heatmap(z=z,x=labs,y=labs,text=text,texttemplate="%{text}",colorscale="RdBu",zmin=-1,zmax=1,colorbar=dict(title="ρ"),hovertemplate="%{y} vs %{x}<br>ρ=%{z:.3f}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    figs.append(("fig08_spearman",style(fig,False,680),"8. Correlaciones Spearman no redundantes con control FDR" if ES else "8. Non-redundant Spearman correlations with FDR control"))

    # 9 PCA: label only most distant observations, variance in axes
    fig=go.Figure()
    if not pca_scores.empty:
        p=pca_scores.copy();p["distance"]=np.sqrt(p.PC1**2+p.PC2**2);p["country_name"]=p.country.apply(country_name_from_code);top=set(p.nlargest(18,"distance").country);p["label"]=p.country.where(p.country.isin(top),"")
        ev=pca_scores.attrs.get("explained_variance_ratio",[np.nan,np.nan]);xlab=f"PC1 ({ev[0]*100:.1f}%)" if pd.notna(ev[0]) else "PC1";ylab=f"PC2 ({ev[1]*100:.1f}%)" if pd.notna(ev[1]) else "PC2"
        fig.add_trace(go.Scatter(x=p.PC1,y=p.PC2,mode="markers+text",text=p.label,textposition="top center",marker=dict(size=9,color=PALETTE[0],opacity=.75,line=dict(width=.7,color="white")),customdata=np.stack([p.country_name,p.country],axis=1),hovertemplate="%{customdata[0]} (%{customdata[1]})<br>PC1=%{x:.2f}<br>PC2=%{y:.2f}<extra></extra>"))
        fig.update_xaxes(title=xlab);fig.update_yaxes(title=ylab)
    figs.append(("fig09_pca",style(fig,False,620),"9. Posicionamiento multivariado PCA" if ES else "9. Multivariate PCA positioning"))

    # 10 Clusters: selective labels and meaningful legend
    fig=go.Figure()
    if not clusters.empty and not pca_scores.empty:
        z=pca_scores.merge(clusters,on="country");z["distance"]=np.sqrt(z.PC1**2+z.PC2**2);top=set(z.nlargest(16,"distance").country);z["label"]=z.country.where(z.country.isin(top),"")
        for idx,(cl,g) in enumerate(z.groupby("cluster")):
            fig.add_trace(go.Scatter(x=g.PC1,y=g.PC2,mode="markers+text",text=g.label,textposition="top center",name=f"Cluster {int(cl)}",marker=dict(size=10,color=PALETTE[idx%len(PALETTE)],line=dict(width=.8,color="white"),opacity=.82),hovertext=[country_name_from_code(c) for c in g.country],hoverinfo="text"))
        ev=pca_scores.attrs.get("explained_variance_ratio",[np.nan,np.nan]);fig.update_xaxes(title=f"PC1 ({ev[0]*100:.1f}%)" if pd.notna(ev[0]) else "PC1");fig.update_yaxes(title=f"PC2 ({ev[1]*100:.1f}%)" if pd.notna(ev[1]) else "PC2")
    figs.append(("fig10_clusters",style(fig,True,620),"10. Tipologías empíricas de países" if ES else "10. Empirical country typologies"))

    # 11 Complete-year trajectories with full country names
    top=orgs.country.value_counts().head(8).index;tq=cy[cy.country.isin(top)].copy();tq["country_name"]=tq.country.apply(country_name_from_code)
    fig=px.line(tq,x="start_year",y="projects",color="country_name",markers=True,color_discrete_sequence=PALETTE)
    fig.update_traces(line=dict(width=2.5),marker=dict(size=5));fig.update_xaxes(title="Año" if ES else "Year",dtick=2);fig.update_yaxes(title="Proyectos" if ES else "Projects")
    figs.append(("fig11_country_trajectories",style(fig,True,600),"11. Trayectorias longitudinales por país" if ES else "11. Longitudinal country trajectories"))

    # 12 Persistence survival profile instead of vertical pile-up
    fig=go.Figure()
    if not pairs.empty:
        pp=pairs.dropna(subset=["active_years","shared_projects"]).copy();maxy=int(pp.active_years.max());ths=np.arange(1,maxy+1)
        link_surv=[(pp.active_years>=t).mean() for t in ths]
        total=pp.shared_projects.sum();vol_surv=[pp.loc[pp.active_years>=t,"shared_projects"].sum()/total if total>0 else np.nan for t in ths]
        fig.add_trace(go.Scatter(x=ths,y=link_surv,mode="lines+markers",name="Bilateral links",line=dict(width=3,color=PALETTE[0])))
        fig.add_trace(go.Scatter(x=ths,y=vol_surv,mode="lines+markers",name="Collaboration volume",line=dict(width=3,color=PALETTE[1])))
        med=int(pp.active_years.median());fig.add_vline(x=med,line_dash="dot",line_color="#7A8793");fig.add_annotation(x=med,y=.08,text=f"Median={med} years",showarrow=False,font=dict(size=12))
    fig.update_xaxes(title="Persistencia mínima (años)" if ES else "Minimum persistence (years)",dtick=1)
    fig.update_yaxes(title="Proporción superviviente" if ES else "Surviving share",tickformat=".0%",range=[0,1.02])
    figs.append(("fig12_persistence_survival",style(fig,True,580),"12. Supervivencia de las alianzas internacionales" if ES else "12. International partnership survival"))

    ont=ontology_figure(lang);ont.update_layout(font=dict(family="Times New Roman",size=13,color="#17324D"),title=None)
    figs.append(("fig13_ontology",ont,"13. Ontology" if lang=="EN" else "13. Ontología"))
    return figs

def package_all_figures_en(figs):
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,"w",zipfile.ZIP_DEFLATED) as z:
        manifest=[]
        for stem, fig, label in figs:
            f=go.Figure(fig)
            f.update_layout(title=None,font=dict(family="Times New Roman",size=13,color="#17324D"))
            pdf=f.to_image(format="pdf")
            z.writestr(f"{stem}.pdf", pdf)
            manifest.append({"file":f"{stem}.pdf","label_en":label})
        z.writestr("manifest_figures_en.csv", pd.DataFrame(manifest).to_csv(index=False))
    mem.seek(0)
    return mem.getvalue()

# ---------- UI ----------
lang=st.sidebar.radio("Language / Idioma",["ES","EN"],horizontal=True)
st.sidebar.success(f"Research Partnership Atlas v{APP_VERSION}")
ES=lang=="ES"
st.title("Research Partnership Atlas · " + ("HMI ejecutivo de colaboración internacional y fondos externos" if ES else "Executive HMI for international collaboration and external funding"))
st.caption("CORDIS Horizon Europe + Horizon 2020 · datos observados + métricas derivadas" if ES else "CORDIS Horizon Europe + Horizon 2020 · observed data + derived metrics")
programmes=st.sidebar.multiselect("Programas / Programmes",["HORIZON","H2020"],default=["HORIZON","H2020"])

if "projects" not in st.session_state:
    seed=pd.read_csv(SEED_FILE)
    seed["project_id"]=seed["id"];seed["project_title"]=seed["title"];seed["framework_programme"]=seed["frameworkProgramme"]
    seed["start_date"]=pd.to_datetime(seed["startDate"]);seed["start_year"]=seed["start_date"].dt.year
    seed["end_date"]=pd.to_datetime(seed["endDate"])
    seed["total_cost"]=pd.to_numeric(seed["totalCost"],errors="coerce")
    seed["ec_max_contribution"]=pd.to_numeric(seed["ecMaxContribution"],errors="coerce")
    seed["funding_scheme"]=seed["fundingScheme"];seed["topic"]=seed["topics"];seed["grant_doi"]=seed["grantDoi"]
    st.session_state.projects=seed[["project_id","acronym","project_title","start_date","end_date","start_year","total_cost","ec_max_contribution","funding_scheme","topic","grant_doi","status","framework_programme","source_system","record_status"]]
    st.session_state.orgs=pd.DataFrame()
    st.session_state.audit=pd.DataFrame([{"programme":"SEED","projects":len(seed),"participations":0,"status":"REAL_CORDIS_SAMPLE"}])

st.info("El CSV incluido es real pero pequeño. Las 12 figuras analíticas se habilitan únicamente después de descargar CORDIS completo." if ES else
        "The bundled CSV is real but small. The 12 analytical figures are enabled only after downloading full CORDIS data.")

if st.sidebar.button("Descargar / actualizar CORDIS completo" if ES else "Download / refresh full CORDIS data",type="primary",use_container_width=True):
    try:
        with st.spinner("CORDIS bulk CSV..."):
            p,o,a=full_data(programmes)
        st.session_state.projects=p;st.session_state.orgs=o;st.session_state.audit=a
        st.success(f"{len(p):,} projects · {len(o):,} participations")
    except Exception as e:
        st.error(f"CORDIS: {e}")
        st.warning("No se generaron datos de sustitución." if ES else "No replacement data were generated.")

projects=st.session_state.projects.copy()
orgs=st.session_state.orgs.copy()

# Analysis period: complete calendar years by default to avoid artificial end-of-series drops.
valid_years=pd.to_numeric(projects.get("start_year"),errors="coerce").dropna().astype(int)
if not valid_years.empty:
    raw_min=int(valid_years.min());raw_max=int(valid_years.max())
    last_complete=datetime.now().year-1
    default_max=min(raw_max,last_complete)
    default_min=max(raw_min,2014)
    complete_only=st.sidebar.checkbox("Solo años completos / Complete years only",value=True)
    max_allowed=default_max if complete_only else raw_max
    if default_min>max_allowed:default_min=raw_min
    yrange=st.sidebar.slider("Rango analítico / Analysis years",min_value=raw_min,max_value=max_allowed,value=(default_min,max_allowed))
    projects=projects[projects.start_year.between(yrange[0],yrange[1],inclusive="both")].copy()
    if not orgs.empty:
        valid_pids=set(projects.project_id)
        orgs=orgs[orgs.project_id.isin(valid_pids)].copy()

countries=sorted(orgs["country"].dropna().unique().tolist()) if not orgs.empty else []
country_options = [{"code": c, "label": country_label(c)} for c in countries]
country_options = sorted(country_options, key=lambda x: x["label"])

available_regions = []
for region_name, region_codes in REGION_PRESETS.items():
    if set(countries).intersection(region_codes):
        available_regions.append(region_name)

region_display = {
    r: (REGION_LABEL_ES.get(r, r) if ES else r)
    for r in available_regions
}
display_to_region = {v: k for k, v in region_display.items()}

selected_region_labels = st.sidebar.multiselect(
    "Filtros regionales rápidos / Quick regional filters",
    options=[region_display[r] for r in available_regions],
    default=[]
)
selected_regions = [display_to_region[x] for x in selected_region_labels]

region_codes_selected = sorted(set(
    code for region in selected_regions
    for code in REGION_PRESETS.get(region, [])
    if code in countries
))
region_labels_selected = [country_label(code) for code in region_codes_selected]
if selected_regions:
    st.sidebar.caption(
        f"Countries added by region: {len(region_codes_selected)}"
    )

sel_labels = st.sidebar.multiselect(
    "Países focales / Focal countries",
    options=[x["label"] for x in country_options],
    default=region_labels_selected
)
label_to_code = {x["label"]: x["code"] for x in country_options}
sel = [label_to_code[s] for s in sel_labels if s in label_to_code]
if sel and not orgs.empty:
    pids=set(orgs.loc[orgs.country.isin(sel),"project_id"])
    orgs=orgs[orgs.project_id.isin(pids)]
    projects=projects[projects.project_id.isin(pids)]

edges=build_edges(orgs,projects)
cy=country_year_table(orgs,projects)
cm,G=country_metrics(orgs,projects,edges) if not orgs.empty else (pd.DataFrame(),nx.Graph())
cons=consortium_sizes(orgs)
pairs=pair_persistence(edges)
annual=annual_growth(cy)
pca_scores,pca_load,pca_note=pca_analysis(cm) if not cm.empty else (pd.DataFrame(),pd.DataFrame(),"")
clusters,cluster_note=cluster_analysis(cm) if not cm.empty else (pd.DataFrame(),"")
if not cm.empty and not clusters.empty:
    cm=cm.merge(clusters,on="country",how="left")

k1,k2,k3,k4,k5,k6=st.columns(6)
k1.metric("Projects",f"{projects.project_id.nunique():,}")
k2.metric("Participations",f"{len(orgs):,}")
k3.metric("Countries",f"{orgs.country.nunique() if not orgs.empty else 0:,}")
k4.metric("EC funding",f"€{orgs.ec_contribution.fillna(0).sum()/1e9:.2f}B" if not orgs.empty else "—")
k5.metric("Network density",f"{nx.density(G):.3f}" if G.number_of_nodes()>1 else "—")
k6.metric("Funding Gini",f"{gini(cm.ec_funding):.3f}" if not cm.empty else "—")

en_figs = build_figures(projects, orgs, annual, cm, G, cons, pairs, cy, pca_scores, pca_load, pca_note, clusters, cluster_note, lang="EN") if not orgs.empty else []
ui_figs = build_figures(projects, orgs, annual, cm, G, cons, pairs, cy, pca_scores, pca_load, pca_note, clusters, cluster_note, lang=("ES" if ES else "EN")) if not orgs.empty else []

tabs=st.tabs(["12 analyses","Ontology","Statistical results","Data & audit","Figure package"])

with tabs[0]:
    if orgs.empty:
        st.warning("Descargue CORDIS completo: no se construyen análisis científicos a partir de cinco registros semilla." if ES else
                   "Download full CORDIS data: scientific analyses are not built from the five-record seed.")
    else:
        for i,(stem,fig,label) in enumerate(ui_figs[:12], start=1):
            st.subheader(label)
            if stem == "fig09_pca" and pca_note:
                st.caption(pca_note)
            if stem == "fig10_clusters" and cluster_note:
                st.caption(cluster_note)
            st.plotly_chart(fig,use_container_width=True)
            export(fig, stem, f"a{i}")

with tabs[1]:
    if orgs.empty:
        st.warning("Ontology export becomes active after full CORDIS download." if not ES else "La exportación de la ontología se activa después de descargar CORDIS completo.")
    else:
        stem, fig, label = ui_figs[12]
        st.plotly_chart(fig,use_container_width=True)
        export(fig, stem, "ont")
        st.caption("Figura conceptual adicional; no se contabiliza entre los 12 resultados analíticos." if ES else
                   "Additional conceptual figure; not counted among the 12 analytical results.")

with tabs[2]:
    if not orgs.empty:
        st.subheader("Métricas de país / Country metrics")
        st.dataframe(cm,use_container_width=True)
        st.subheader("PCA loadings")
        st.dataframe(pca_load,use_container_width=True)
        st.subheader("Pair persistence")
        st.dataframe(pairs.head(500),use_container_width=True)
        st.info(("Las métricas son descriptivas/derivadas. PCA y clustering solo se calculan cuando hay suficientes países completos. "
                 "No se interpreta asociación como causalidad.") if ES else
                ("Metrics are descriptive/derived. PCA and clustering are only computed with enough complete countries. "
                 "Associations are not interpreted as causal."))

with tabs[3]:
    st.dataframe(st.session_state.audit,use_container_width=True)
    if not orgs.empty:
        analyzed=orgs.merge(projects,on=["project_id","framework_programme"],how="left",suffixes=("","_project"))
        analyzed=analyzed.merge(cm,on="country",how="left")
        analyzed["analysis_version"]=APP_VERSION
        analyzed["analysis_generated_at_utc"]=datetime.now(timezone.utc).isoformat()
        analyzed["analysis_origin"]="CORDIS observed bulk data + transparent derived metrics"
        st.download_button("Descargar CSV analizado" if ES else "Download analyzed CSV",
            analyzed.to_csv(index=False).encode("utf-8-sig"),
            file_name="research_partnership_atlas_analysed_cordis_v1.csv",mime="text/csv",type="primary")
        st.download_button("Country metrics CSV",cm.to_csv(index=False).encode("utf-8-sig"),file_name="country_metrics_v1.csv",mime="text/csv")
        st.download_button("Pair persistence CSV",pairs.to_csv(index=False).encode("utf-8-sig"),file_name="pair_persistence_v1.csv",mime="text/csv")
        if not pca_load.empty:
            st.download_button("PCA loadings CSV",pca_load.to_csv(index=False).encode("utf-8-sig"),file_name="pca_loadings_v1.csv",mime="text/csv")
    else:
        st.download_button("CSV real incluido",SEED_FILE.read_bytes(),file_name="cordis_real_seed.csv",mime="text/csv")

with tabs[4]:
    if orgs.empty:
        st.warning("Descargue CORDIS completo para generar el paquete de figuras." if ES else
                   "Download full CORDIS data to generate the figure package.")
    else:
        st.markdown("**English figure package**")
        st.caption("13 PDFs in English, Times New Roman 13 pt, no figure titles. Includes the 12 analytical figures plus the ontology.")
        try:
            zip_bytes = package_all_figures_en(en_figs)
            st.download_button(
                "Download ZIP of English PDF figures" if not ES else "Descargar ZIP de figuras PDF en inglés",
                zip_bytes,
                file_name="research_partnership_atlas_v1_english_figures_pdf.zip",
                mime="application/zip",
                type="primary"
            )
            st.success("Package ready: English PDF figures, no titles, TNR 13 pt.")
        except Exception as e:
            st.error(f"Figure package export error: {e}")
            st.info("Ensure Kaleido is installed from requirements.txt.")

st.caption(f"Research Partnership Atlas v{APP_VERSION} · 12 data-driven analyses · English PDF figure package · no bar charts · no synthetic data")
