"""V3-F: audited, match-filter-scoped IPL franchise reports.

Pure report calculations are shared between the Streamlit preview, PDF, and
CSV evidence exports.  No new model predictions or invented trophy/captain data.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from html import escape
from io import BytesIO
import json
import re
import zipfile

import numpy as np
import pandas as pd
from dashboard.analytics import TEAMS, ALL_TEAMS, PHASE_ORDER
from dashboard.franchise_analytics import (
    TeamSelection, select_team_matches, team_scope, count_stats,
    playoff_history, player_leaders, phase_table, opponents_table,
    venues_table, analyst_brief,
)

SOURCE = 'IPL Intelligence 360 - Cricsheet-derived IPL match and delivery tables (2008-2026)'

@dataclass
class ReportSnapshot:
    code: str
    selection: TeamSelection
    team_name: str
    matches: pd.DataFrame
    stats: dict
    all_time_titles: list[int]
    seasons: pd.DataFrame
    batting: pd.DataFrame
    bowling: pd.DataFrame
    bat_phase: pd.DataFrame
    bowl_phase: pd.DataFrame
    opponents: pd.DataFrame
    venues: pd.DataFrame
    notes: list[str]

    @property
    def is_small_sample(self):
        return int(self.stats['decided']) < 20

    @property
    def filter_labels(self):
        s=self.selection
        return {
            'Seasons': str(s.year_min) if s.year_min==s.year_max else f'{s.year_min}-{s.year_max}',
            'Opponent': ', '.join(s.opponents) if s.opponents else 'All opponents',
            'Venue': ', '.join(s.venues) if s.venues else 'All venues',
            'Match stage': ', '.join(s.stages) if s.stages else 'All stages',
            'Match result': s.outcome,
            'Innings role': s.innings,
            'Toss result': s.toss,
        }


def build_snapshot(selection:TeamSelection, *, matches:pd.DataFrame,
                   team_matches:pd.DataFrame, innings:pd.DataFrame,
                   phase_match:pd.DataFrame, bat_match:pd.DataFrame,
                   bowl_match:pd.DataFrame)->ReportSnapshot:
    if selection.team not in TEAMS:
        raise ValueError('Unknown active franchise code')
    if selection.player_id is not None:
        raise ValueError('Player participant filter is not supported by the PDF studio')
    picked=select_team_matches(team_matches,selection)
    if picked.empty:
        raise ValueError('No recorded IPL matches match this selection')
    scope=team_scope(picked.match_id.unique(),selection.team,innings,phase_match,bat_match,bowl_match)
    stats=count_stats(picked,scope)
    hist=playoff_history(matches,selection.team)
    titles=(hist.loc[hist.champion,'season'].astype(int).tolist() if len(hist) else [])
    leaders=player_leaders(scope['bat'],scope['bowl'])
    decided=picked[picked.is_decided.astype(bool)].copy()
    if decided.empty:
        season=pd.DataFrame(columns=['season_year','matches','wins','losses','win_pct'])
    else:
        season=decided.groupby('season_year').agg(matches=('match_id','size'),wins=('won','sum'),losses=('lost','sum')).reset_index()
        season['win_pct']=100*season.wins/season.matches
    # A benchmark across the same selected match universe; it is not a
    # league-wide average over other matches/years.
    notes=analyst_brief(picked,scope,scope,selection.team)
    return ReportSnapshot(selection.team,selection,TEAMS[selection.team][0],picked,stats,
        titles,season,leaders['batting'],leaders['bowling'],
        phase_table(scope['bat_phase']),phase_table(scope['bowl_phase']),
        opponents_table(picked),venues_table(picked),notes)


def _safe_percent(value):
    return f'{value:.1f}%' if pd.notna(value) and np.isfinite(value) else 'N/A'


def _clean_text(s):
    # analyst_brief produces trusted lightweight Markdown; avoid showing raw ** in PDFs
    return re.sub(r'\*\*','',str(s)).replace('–','-').replace('—','-')


def manifest(snapshot:ReportSnapshot)->dict:
    return {
        'product':'IPL Intelligence 360 - V3-F Analyst Report Studio',
        'generated_on_utc_date':date.today().isoformat(),
        'franchise':snapshot.code,'franchise_name':snapshot.team_name,
        'filters':snapshot.filter_labels,
        'match_count':len(snapshot.matches),
        'decided_match_count':int(snapshot.stats['decided']),
        'match_ids':sorted(int(x) for x in snapshot.matches.match_id),
        'source':SOURCE,
        'definitions':{
          'match_win_rate':'Wins divided by decided games (abandoned/no-result excluded).',
          'scoring_run_rate':'Regulation runs scored per six legal deliveries in the selected matches.',
          'batting_phase':'Powerplay, middle and death overs, from legal-delivery match phase data.',
          'all_time_trophies':'IPL finals won by the franchise; NOT restricted to active match filters.',
          'player_leaderboards':'Runs/wickets aggregated across the selected matches; not career totals.',
          'team_participants':'Neither inferred captains nor inferred starting XIs are used.',
          'causality':'Correlations and apparent team strengths do not establish causal impacts.',
        },
        'warning':'Retrospective EDA only. Not a betting recommendation, match forecast, or model validation.',
    }


def evidence_zip(snapshot:ReportSnapshot,pdf_bytes:bytes|None=None)->bytes:
    files={
        'evidence/selected_team_matches.csv':snapshot.matches.to_csv(index=False).encode('utf-8'),
        'evidence/season_results.csv':snapshot.seasons.to_csv(index=False).encode('utf-8'),
        'evidence/batting_leaders.csv':snapshot.batting.to_csv(index=False).encode('utf-8'),
        'evidence/bowling_leaders.csv':snapshot.bowling.to_csv(index=False).encode('utf-8'),
        'evidence/batting_phases.csv':snapshot.bat_phase.to_csv(index=False).encode('utf-8'),
        'evidence/bowling_phases.csv':snapshot.bowl_phase.to_csv(index=False).encode('utf-8'),
        'evidence/opponents.csv':snapshot.opponents.to_csv(index=False).encode('utf-8'),
        'evidence/venues.csv':snapshot.venues.to_csv(index=False).encode('utf-8'),
        'evidence/report_manifest.json':json.dumps(manifest(snapshot),indent=2,ensure_ascii=False).encode('utf-8'),
    }
    if pdf_bytes:
        files[f'IPL360_{snapshot.code}_Analyst_Report.pdf']=pdf_bytes
    buf=BytesIO()
    with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for key,content in files.items():z.writestr(key,content)
    return buf.getvalue()


def generate_pdf(snapshot:ReportSnapshot)->bytes:
    """Generate a deterministic, branded multi-page PDF entirely in memory."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Table, TableStyle,
        Spacer, KeepTogether, PageBreak,
    )
    from reportlab.graphics.shapes import Drawing,Rect,String,Line

    buff=BytesIO(); ink=colors.HexColor('#182A43');muted=colors.HexColor('#5B6E83')
    from pathlib import Path
    from dashboard.data import ROOT
    theme=json.loads((ROOT/'assets/team_theme_tokens.json').read_text())
    accent_hex=str(theme['teams'][snapshot.code]['primary'])
    accent=colors.HexColor(accent_hex)
    bg=colors.HexColor('#EDF3FA')
    doc=SimpleDocTemplate(buff,pagesize=A4,rightMargin=38,leftMargin=38,
                          topMargin=56,bottomMargin=48,title=f'{snapshot.team_name} - IPL Analyst Report',
                          author='IPL Intelligence 360')
    usable=A4[0]-76
    normal=getSampleStyleSheet()
    styles={
      'h1':ParagraphStyle('IPLH1',parent=normal['Heading1'],fontName='Helvetica-Bold',fontSize=20,leading=24,textColor=ink,spaceAfter=8),
      'h2':ParagraphStyle('IPLH2',parent=normal['Heading2'],fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=ink,spaceBefore=15,spaceAfter=7),
      'text':ParagraphStyle('IPLT',parent=normal['BodyText'],fontName='Helvetica',fontSize=8.8,leading=13,textColor=ink,spaceAfter=6),
      'small':ParagraphStyle('IPLS',parent=normal['BodyText'],fontName='Helvetica',fontSize=7.6,leading=11,textColor=muted,spaceAfter=5),
      'cell':ParagraphStyle('IPLC',parent=normal['BodyText'],fontName='Helvetica',fontSize=8.5,leading=11,textColor=ink),
    }
    P=lambda txt,which='text':Paragraph(escape(_clean_text(txt)),styles[which])
    def table(rows, colwidths, header=True):
        item=Table([[P(x,'cell') for x in row] for row in rows],colWidths=colwidths,repeatRows=1 if header else 0,hAlign='LEFT')
        commands=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),
                  ('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#D8E1EA'))]
        if header:commands += [('BACKGROUND',(0,0),(-1,0),bg),('LINEBELOW',(0,0),(-1,0),.8,accent)]
        for idx in range(1 if header else 0,len(rows)):
            if idx%2==0:commands.append(('BACKGROUND',(0,idx),(-1,idx),colors.HexColor('#F7F9FC')))
        item.setStyle(TableStyle(commands));return item
    def bars(data,title,w=usable,h=155):
        """Simple editable vector bars; labels use real match-scoped measurements."""
        chart=Drawing(w,h)
        chart.add(String(1,h-15,title,fontSize=10,fontName='Helvetica-Bold',fillColor=ink))
        if not data:
            chart.add(String(5,h/2,'Not enough observations',fontSize=9,fillColor=muted));return chart
        plot_w=w-150; x0=85; top=h-40; step=(h-47)/len(data)
        maxi=max(v for _,v in data) or 1
        for idx,(lab,value) in enumerate(data):
            yy=top-idx*step
            chart.add(String(0,yy+1,str(lab)[:20],fontSize=8,fillColor=muted))
            chart.add(Rect(x0,yy-2,max(0,value/maxi*plot_w),min(12,step*.55),fillColor=accent,strokeColor=None))
            chart.add(String(w-8, yy,str(round(value,1)),fontSize=8,fillColor=ink,textAnchor='end'))
        return chart
    def section(title):story.append(P(title,'h2'))
    story=[P(f'{snapshot.team_name} | Sports Analyst Report','h1'),
           P(f'IPL INTELLIGENCE 360  /  {snapshot.code}  /  Historical match evidence  /  {date.today().isoformat()}','small')]
    filter_bits=[f'{k}: {v}' for k,v in snapshot.filter_labels.items()]
    story.append(P('ACTIVE ANALYSIS FILTERS','h2'))
    story.append(P('  |  '.join(filter_bits),'small'))
    s=snapshot.stats
    title_note=(', '.join(str(t) for t in snapshot.all_time_titles) if snapshot.all_time_titles else 'None recorded')
    cards=[
       ('Matches analyzed',str(s['matches'])),('Wins',str(s['wins'])),('Decided matches',str(s['decided'])),
       ('Match win rate',_safe_percent(s['win_pct'])),
       ('Runs scored',f"{s['runs_scored']:,}"),('Batting run rate',f"{s['batting_rr']:.2f}" if pd.notna(s['batting_rr']) else 'N/A'),
       ('Wickets taken',str(s['wickets_taken'])),('Bowling runs/over',f"{s['bowling_rr']:.2f}" if pd.notna(s['bowling_rr']) else 'N/A')]
    story.append(table([cards[i:i+2] if False else [f'{cards[i][0]}: {cards[i][1]}', f'{cards[i+1][0]}: {cards[i+1][1]}'] for i in range(0,len(cards),2)], [usable/2]*2,header=False))
    story.append(P(f'IPL championships (all-time, outside selected filters): {len(snapshot.all_time_titles)}. Trophy seasons: {title_note}.','small'))
    if snapshot.is_small_sample:
        story.append(P(f'SAMPLE WARNING: only {s["decided"]} decided matches. Treat rankings and trends cautiously.','small'))
    section('Match results by season')
    trend=snapshot.seasons
    story.append(bars([(str(int(r.season_year)),float(r.win_pct)) for r in trend.tail(10).itertuples()],
                      'Team win percentage for selected seasons'))
    story.append(P('Win rate uses decided matches only; the chart includes at most the last 10 seasons within your filters.','small'))
    story.append(PageBreak())
    story.append(P('Batting, bowling & match intelligence','h1'))
    topbat=snapshot.batting.head(5)
    section('Leading run scorers - selected matches')
    if len(topbat):
        story.append(table([['Player','Runs','Balls','Strike rate']]+[[str(r.player_name),str(int(r.runs)),str(int(r.balls)),
            f'{r.strike_rate:.1f}' if pd.notna(r.strike_rate) else '-'] for r in topbat.itertuples()],
            [usable*.43,usable*.17,usable*.17,usable*.23]))
    else:story.append(P('No batting records for this selection.'))
    topbowl=snapshot.bowling.head(5)
    section('Leading wicket takers - selected matches')
    if len(topbowl):
        story.append(table([['Player','Wickets','Balls','Economy']]+[[str(r.player_name),str(int(r.wickets)),str(int(r.balls)),
            f'{r.economy:.2f}' if pd.notna(r.economy) else '-'] for r in topbowl.itertuples()],
            [usable*.43,usable*.17,usable*.17,usable*.23]))
    else:story.append(P('No bowling records for this selection.'))
    phase=snapshot.bat_phase.dropna(subset=['run_rate'])
    if len(phase):
        section('Batting run rate by innings phase')
        story.append(bars([(str(r.phase).split(' (')[0],float(r.run_rate)) for r in phase.itertuples()],
                          'Runs scored per 6 legal balls by innings phase',h=125))
    story.append(PageBreak())
    story.append(P('Rivalries, insights & audit trail','h1'))
    opp=snapshot.opponents.head(7)
    section('Opposition record - decided matches')
    if len(opp):
        story.append(table([['Opponent','Matches','Won','Win %']]+[[str(r.name),str(int(r.matches)),str(int(r.wins)),f'{r.win_pct:.1f}%'] for r in opp.itertuples()],
            [usable*.43,usable*.17,usable*.17,usable*.23]))
    else:story.append(P('No decided opposition records for these filters.'))
    section('Sports analyst briefing')
    for note in snapshot.notes[:5]:story.append(P('- '+note))
    section('Data provenance & interpretation')
    story.extend([
        P(f'Source: {SOURCE}','small'),
        P(f'Selected team-match rows: {len(snapshot.matches)}. Every report KPI, selected-match leaderboard, and insight is calculated from the same selected match IDs.','small'),
        P('All-time IPL trophies are intentionally not affected by page filters. CLT20 trophies are NOT included in IPL titles.','small'),
        P('Win percentages exclude undecided matches. Phase figures exclude super-over play. Players listed in a match are not assumed to be captains or confirmed starting XI.','small'),
        P('This is retrospective sports analysis, not a prediction. Opponent, venue and team selection can introduce confounding and small-sample effects.','small'),
        P('Download the companion Evidence ZIP for selected match IDs, season data, player leaders, phase tables, and filter manifest.','small'),
    ])
    def header_footer(canvas,doc):
        canvas.saveState()
        ww,hh=A4
        canvas.setFillColor(colors.HexColor('#0C1A30'))
        canvas.rect(0,hh-32,ww,32,fill=1,stroke=0)
        canvas.setFillColor(accent)
        canvas.setFont('Helvetica-Bold',9)
        canvas.drawString(38,hh-20,'IPL INTELLIGENCE 360°  /  ANALYST REPORTS')
        canvas.setStrokeColor(colors.HexColor('#D9E4EF'))
        canvas.line(38,36,ww-38,36)
        canvas.setFillColor(muted);canvas.setFont('Helvetica',8)
        canvas.drawString(38,23,f'{snapshot.code}  |  Historical IPL analysis  |  {date.today().isoformat()}')
        canvas.drawRightString(ww-38,23,f'Page {doc.page}')
        canvas.restoreState()
    doc.build(story,onFirstPage=header_footer,onLaterPages=header_footer)
    return buff.getvalue()
