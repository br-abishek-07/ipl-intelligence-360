"""Reusable sports-analytics calculations; independent of Streamlit."""
import numpy as np
import pandas as pd

TEAMS={
 'CSK':('Chennai Super Kings','#F6C445'), 'MI':('Mumbai Indians','#2978B5'),
 'RCB':('Royal Challengers Bengaluru','#C83843'), 'KKR':('Kolkata Knight Riders','#9775CF'),
 'SRH':('Sunrisers Hyderabad','#F58B36'), 'RR':('Rajasthan Royals','#E879B7'),
 'DC':('Delhi Capitals','#578CE6'), 'PBKS':('Punjab Kings','#F06A6A'),
 'GT':('Gujarat Titans','#66C2C5'), 'LSG':('Lucknow Super Giants','#64C9E8')
}
TEAM_LABELS={k:v[0] for k,v in TEAMS.items()}
ALL_TEAMS={**TEAM_LABELS,'DCH':'Deccan Chargers (historic)','GL':'Gujarat Lions (historic)','KTK':'Kochi Tuskers Kerala (historic)','PWI':'Pune Warriors India (historic)','RPS':'Rising Pune Supergiant (historic)'}
PHASE_ORDER=['Powerplay (1–6)','Middle (7–15)','Death (16–20)']

def filter_year(df, years):
    if df is None: return None
    if not years: return df
    lo,hi=years
    return df.loc[df.season_year.between(lo,hi)].copy()

def win_rate(rows):
    decided=rows.loc[rows.is_decided.astype(bool)]
    return float(decided.won.mean()) if len(decided)>0 else np.nan

def franchise_seasons(tm,code):
    t=tm[tm.team_code==code]
    if t.empty:return pd.DataFrame(columns=['season_year','played','decided','won','win_pct'])
    out=t.groupby('season_year').agg(played=('match_id','size'),decided=('is_decided','sum'),won=('won','sum')).reset_index()
    out['win_pct']=100*out.won/out.decided.replace(0,np.nan)
    return out.sort_values('season_year')

def matchup_table(tm,code):
    t=tm[(tm.team_code==code)&tm.is_decided.astype(bool)]
    if t.empty:return pd.DataFrame(columns=['opponent_code','matches','wins','win_pct'])
    x=t.groupby('opponent_code').agg(matches=('match_id','size'),wins=('won','sum')).reset_index()
    x['win_pct']=100*x.wins/x.matches.replace(0,np.nan)
    return x.sort_values(['matches','win_pct'],ascending=[False,False])

def venue_table(tm,code=None,min_sample=1):
    t=tm[tm.is_decided.astype(bool)]
    if code:t=t[t.team_code==code]
    x=t.groupby('venue_group').agg(matches=('match_id','size'),wins=('won','sum') if code else ('won','sum')).reset_index()
    x=x[x.matches>=min_sample].copy()
    if code:x['win_pct']=100*x.wins/x.matches
    else:x=x.drop(columns=['wins'])
    return x.sort_values('matches',ascending=False)

def phase_metrics(phase, years=None, team=None, orientation='bat'):
    p=filter_year(phase,years)
    if team:
        p=p[(p.batting_team if orientation=='bat' else p.bowling_team)==team]
    if p.empty: return pd.DataFrame(columns=['phase','runs','legal_balls','wickets','run_rate','wickets_per_120'])
    g=p.groupby('phase',observed=True).agg(runs=('runs','sum'),legal_balls=('legal_balls','sum'),wickets=('wickets','sum'),fours=('fours','sum'),sixes=('sixes','sum')).reindex(PHASE_ORDER).reset_index()
    g['run_rate']=6*g.runs/g.legal_balls.replace(0,np.nan)
    g['wickets_per_120']=120*g.wickets/g.legal_balls.replace(0,np.nan)
    return g

def top_batters(bat,code,years=None,limit=10,min_balls=30):
    x=filter_year(bat,years)
    x=x[x.team_code==code]
    if x.empty:return x
    g=x.groupby('player_id',dropna=False).agg(player_name=('player_name','last'),seasons=('season_year','nunique'),matches=('matches','sum'),runs=('runs','sum'),balls=('balls','sum'),fours=('fours','sum'),sixes=('sixes','sum')).reset_index()
    g['strike_rate']=100*g.runs/g.balls.replace(0,np.nan)
    return g[g.balls>=min_balls].sort_values('runs',ascending=False).head(limit)

def top_bowlers(bowl,code,years=None,limit=10,min_balls=36):
    x=filter_year(bowl,years)
    x=x[x.team_code==code]
    if x.empty:return x
    g=x.groupby('player_id',dropna=False).agg(player_name=('player_name','last'),seasons=('season_year','nunique'),matches=('matches','sum'),wickets=('wickets','sum'),balls=('balls','sum'),runs_conceded=('runs_conceded','sum')).reset_index()
    g['economy']=6*g.runs_conceded/g.balls.replace(0,np.nan)
    return g[g.balls>=min_balls].sort_values(['wickets','economy'],ascending=[False,True]).head(limit)

def matchup_h2h(tm,a,b):
    rows=tm[(tm.team_code==a)&(tm.opponent_code==b)&tm.is_decided.astype(bool)]
    return {'matches':len(rows),'a_wins':int(rows.won.sum()),'b_wins':int(rows.lost.sum()),'a_win_rate':win_rate(rows)}

def sport_analyst_notes(tm,phase,bat,bowl,code,years):
    """Only descriptive, conditional inferences backed by visible samples."""
    t=filter_year(tm,years);t=t[t.team_code==code]
    if t.empty:return ['No matches for the selected seasons.']
    decided=t[t.is_decided.astype(bool)]
    notes=[]
    if len(decided)>=5:
        wins=int(decided.won.sum());n=len(decided)
        notes.append(f'**Result efficiency:** {wins} wins in {n} decided matches ({wins/n:.1%}). This is descriptive win rate, not a prediction of the next fixture.')
        first=decided[decided.batted_first.astype(bool)];chase=decided[~decided.batted_first.astype(bool)]
        if len(first)>=5 and len(chase)>=5:
            gap=100*(win_rate(chase)-win_rate(first))
            best='chasing' if gap>0 else 'setting a target'
            notes.append(f'**Innings pattern:** {len(chase)} decided chases versus {len(first)} first-innings attempts; the {best} win rate was higher by {abs(gap):.1f} percentage points. Opposition and venue composition can explain part of this difference.')
    tp=phase_metrics(phase,years,code,'bat');league=phase_metrics(phase,years)
    bp=phase_metrics(phase,years,code,'bowl')
    for kind,frame in [('batting',tp),('bowling',bp)]:
        frame=frame.merge(league[['phase','run_rate']].rename(columns={'run_rate':'league_rate'}),on='phase',how='left')
        if frame.empty:continue
        frame=frame[frame.legal_balls>=120].copy()
        if frame.empty:continue
        frame['differential']=frame.run_rate-frame.league_rate
        if kind=='batting':
            high=frame.sort_values('differential',ascending=False).iloc[0]
            notes.append(f"**Scoring edge:** {high['phase']} batting scored at {high.run_rate:.2f} runs/over versus a league reference of {high.league_rate:.2f} (difference {high.differential:+.2f}), over {int(high.legal_balls)} legal balls.")
        else:
            low=frame.sort_values('differential').iloc[0]
            notes.append(f"**Run prevention:** {low['phase']} bowling conceded {low.run_rate:.2f} runs/over versus the league's {low.league_rate:.2f} (difference {low.differential:+.2f}), across {int(low.legal_balls)} legal balls. Lower is better for the bowling side.")
    vt=venue_table(t,code,min_sample=5)
    if not vt.empty:
        v=vt.iloc[0]
        notes.append(f"**Venue sample:** The most frequent ground is {v.venue_group} ({int(v.matches)} decided matches; {v.win_pct:.1f}% win rate). This is venue association, **not** evidence of a home-ground causal advantage.")
    if len(decided)<10:notes.append('**Small sample warning:** Fewer than 10 resolved results in this selection; percentages can fluctuate substantially.')
    return notes
