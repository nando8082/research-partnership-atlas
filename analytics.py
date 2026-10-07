
import numpy as np
import pandas as pd
import networkx as nx

try:
    from scipy.stats import spearmanr
except Exception:
    spearmanr = None

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
except Exception:
    StandardScaler = PCA = KMeans = silhouette_score = None


def build_edges(orgs, projects):
    if orgs.empty:
        return pd.DataFrame(columns=["country_a","country_b","project_id","year","weight"])
    py = projects[["project_id","start_year"]].drop_duplicates()
    x = orgs.merge(py, on="project_id", how="left")
    rows = []
    for pid, g in x.dropna(subset=["country"]).groupby("project_id"):
        cs = sorted(set(g["country"].dropna().astype(str)))
        yr = g["start_year"].dropna()
        y = int(yr.iloc[0]) if len(yr) else np.nan
        for i in range(len(cs)):
            for j in range(i+1,len(cs)):
                rows.append([cs[i],cs[j],pid,y,1])
    return pd.DataFrame(rows,columns=["country_a","country_b","project_id","year","weight"])


def country_year_table(orgs, projects):
    if orgs.empty:
        return pd.DataFrame()
    p = projects[["project_id","start_year"]].drop_duplicates()
    x = orgs.merge(p,on="project_id",how="left")
    g = x.groupby(["country","start_year"],as_index=False).agg(
        projects=("project_id","nunique"),
        participations=("project_id","size"),
        ec_funding=("ec_contribution","sum"),
        organisations=("organisation_id","nunique")
    )
    return g


def country_metrics(orgs, projects, edges):
    if orgs.empty:
        return pd.DataFrame(), nx.Graph()

    pcounts = orgs.groupby("country")["project_id"].nunique()
    funding = orgs.groupby("country")["ec_contribution"].sum(min_count=1)
    particip = orgs.groupby("country")["project_id"].size()
    orgcount = orgs.groupby("country")["organisation_id"].nunique()
    coord = (
        orgs.assign(is_coord=orgs["role"].astype(str).str.upper().str.contains("COORD",na=False))
        .groupby("country")["is_coord"].mean()*100
    )

    G = nx.Graph()
    if not edges.empty:
        agg = edges.groupby(["country_a","country_b"],as_index=False)["weight"].sum()
        for _,r in agg.iterrows():
            G.add_edge(r.country_a,r.country_b,weight=float(r.weight))

    deg = nx.degree_centrality(G) if G.number_of_nodes() else {}
    btw = nx.betweenness_centrality(G,weight=None,normalized=True) if G.number_of_nodes() else {}
    pr = nx.pagerank(G,weight="weight") if G.number_of_nodes() else {}
    eig = {}
    if G.number_of_nodes():
        try:
            eig = nx.eigenvector_centrality_numpy(G,weight="weight")
        except Exception:
            eig = {n:np.nan for n in G.nodes()}

    pair = pd.DataFrame()
    if not edges.empty:
        pair = edges.groupby(["country_a","country_b"],as_index=False).agg(
            shared_projects=("weight","sum"),
            active_years=("year","nunique")
        )

    partner_sets, persistence, weights = {}, {}, {}
    if not pair.empty:
        for _,r in pair.iterrows():
            for c,p in [(r.country_a,r.country_b),(r.country_b,r.country_a)]:
                partner_sets.setdefault(c,set()).add(p)
                persistence.setdefault(c,[]).append(float(r.active_years))
                weights.setdefault(c,[]).append(float(r.shared_projects))

    rows=[]
    countries=sorted(set(orgs["country"].dropna().astype(str)))
    for c in countries:
        ws=np.asarray(weights.get(c,[]),dtype=float)
        shares=ws/ws.sum() if len(ws) and ws.sum()>0 else np.array([])
        hhi=float((shares**2).sum()) if len(shares) else np.nan
        rows.append({
            "country":c,
            "projects":int(pcounts.get(c,0)),
            "participations":int(particip.get(c,0)),
            "organisations":int(orgcount.get(c,0)),
            "ec_funding":float(funding.get(c,np.nan)),
            "funding_per_project":float(funding.get(c,np.nan))/max(1,int(pcounts.get(c,0))),
            "coordination_share":float(coord.get(c,np.nan)),
            "partner_count":len(partner_sets.get(c,set())),
            "degree":deg.get(c,np.nan),
            "betweenness":btw.get(c,np.nan),
            "pagerank":pr.get(c,np.nan),
            "eigenvector":eig.get(c,np.nan),
            "collaboration_hhi":hhi,
            "diversification":1-hhi if pd.notna(hhi) else np.nan,
            "mean_persistence":float(np.mean(persistence.get(c,[]))) if persistence.get(c) else np.nan,
            "max_persistence":float(np.max(persistence.get(c,[]))) if persistence.get(c) else np.nan,
            "collaboration_weight":float(ws.sum()) if len(ws) else 0.0,
        })
    cm=pd.DataFrame(rows)

    # network communities: deterministic Louvain if available, otherwise greedy modularity
    if G.number_of_nodes() >= 2:
        try:
            communities=nx.community.louvain_communities(G,weight="weight",seed=42)
        except Exception:
            communities=list(nx.community.greedy_modularity_communities(G,weight="weight"))
        cmap={}
        for i,com in enumerate(communities):
            for n in com: cmap[n]=i+1
        cm["community"]=cm["country"].map(cmap)
    else:
        cm["community"]=np.nan

    return cm,G


def gini(values):
    x=np.asarray(pd.Series(values).dropna(),dtype=float)
    x=x[x>=0]
    if len(x)==0 or x.sum()==0: return np.nan
    x=np.sort(x)
    n=len(x)
    return float((2*np.sum(np.arange(1,n+1)*x)/(n*x.sum()))-(n+1)/n)


def spearman_matrix(cm, cols):
    x=cm[cols].apply(pd.to_numeric,errors="coerce")
    return x.corr(method="spearman",min_periods=5)



def _bh_fdr(pvals):
    """Benjamini-Hochberg FDR adjustment for a 1-D array of finite p-values."""
    p=np.asarray(pvals,dtype=float)
    n=len(p)
    order=np.argsort(p)
    ranked=p[order]
    q=ranked*n/np.arange(1,n+1)
    q=np.minimum.accumulate(q[::-1])[::-1]
    q=np.clip(q,0,1)
    out=np.empty_like(q)
    out[order]=q
    return out


def spearman_fdr(cm, cols, min_n=8):
    """Pairwise Spearman rho and BH-FDR q-values; no imputation."""
    x=cm[cols].apply(pd.to_numeric,errors="coerce")
    rho=pd.DataFrame(np.nan,index=cols,columns=cols,dtype=float)
    pmat=pd.DataFrame(np.nan,index=cols,columns=cols,dtype=float)
    tests=[]
    for i,c1 in enumerate(cols):
        rho.loc[c1,c1]=1.0
        pmat.loc[c1,c1]=0.0
        for j in range(i+1,len(cols)):
            c2=cols[j]
            pair=x[[c1,c2]].dropna()
            if len(pair)<min_n or spearmanr is None:
                continue
            r,p=spearmanr(pair[c1],pair[c2])
            rho.loc[c1,c2]=rho.loc[c2,c1]=float(r)
            pmat.loc[c1,c2]=pmat.loc[c2,c1]=float(p)
            tests.append((c1,c2,float(p)))
    qmat=pd.DataFrame(np.nan,index=cols,columns=cols,dtype=float)
    for c in cols:qmat.loc[c,c]=0.0
    if tests:
        qvals=_bh_fdr([t[2] for t in tests])
        for (c1,c2,_),q in zip(tests,qvals):
            qmat.loc[c1,c2]=qmat.loc[c2,c1]=float(q)
    return rho,qmat

def pca_analysis(cm):
    cols=["projects","ec_funding","funding_per_project","coordination_share","partner_count",
          "degree","betweenness","pagerank","diversification","mean_persistence"]
    q=cm[["country"]+cols].replace([np.inf,-np.inf],np.nan).dropna()
    if StandardScaler is None or len(q)<6:
        return pd.DataFrame(), pd.DataFrame(), "Insufficient data for PCA."
    Z=StandardScaler().fit_transform(q[cols])
    p=PCA(n_components=2)
    score=p.fit_transform(Z)
    scores=pd.DataFrame({"country":q["country"].values,"PC1":score[:,0],"PC2":score[:,1]})
    scores.attrs["explained_variance_ratio"] = p.explained_variance_ratio_[:2].tolist()
    loadings=pd.DataFrame({"metric":cols,"PC1_loading":p.components_[0],"PC2_loading":p.components_[1]})
    note=f"Explained variance: PC1={p.explained_variance_ratio_[0]:.3f}, PC2={p.explained_variance_ratio_[1]:.3f}"
    return scores,loadings,note


def cluster_analysis(cm):
    cols=["ec_funding","funding_per_project","coordination_share","partner_count",
          "degree","pagerank","diversification","mean_persistence"]
    q=cm[["country"]+cols].replace([np.inf,-np.inf],np.nan).dropna()
    if StandardScaler is None or len(q)<8:
        return pd.DataFrame(),"Insufficient data for clustering."
    Z=StandardScaler().fit_transform(q[cols])
    max_k=min(6,len(q)-2)
    best=None
    for k in range(2,max_k+1):
        km=KMeans(n_clusters=k,random_state=42,n_init=30)
        lab=km.fit_predict(Z)
        sc=silhouette_score(Z,lab)
        if best is None or sc>best[0]:
            best=(sc,k,lab)
    out=q[["country"]].copy()
    out["cluster"]=best[2]+1
    return out,f"KMeans selected k={best[1]} by maximum silhouette={best[0]:.3f}"


def annual_growth(country_year):
    if country_year.empty: return pd.DataFrame()
    g=country_year.groupby("start_year",as_index=False).agg(projects=("projects","sum"),ec_funding=("ec_funding","sum"))
    g=g.sort_values("start_year")
    g["projects_yoy_pct"]=g["projects"].pct_change()*100
    g["funding_yoy_pct"]=g["ec_funding"].pct_change()*100
    return g


def consortium_sizes(orgs):
    if orgs.empty: return pd.DataFrame()
    return orgs.groupby("project_id",as_index=False).agg(
        organisations=("organisation_id","nunique"),
        countries=("country","nunique"),
        ec_funding=("ec_contribution","sum")
    )


def pair_persistence(edges):
    if edges.empty:return pd.DataFrame()
    return edges.groupby(["country_a","country_b"],as_index=False).agg(
        shared_projects=("weight","sum"),
        active_years=("year","nunique"),
        first_year=("year","min"),
        last_year=("year","max")
    )
