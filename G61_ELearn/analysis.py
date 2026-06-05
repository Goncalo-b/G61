import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

COLORS = ['#334a94','#4f6dd4','#10b981','#f59e0b','#ef4444','#06b6d4','#84cc16']

def _dark_layout(fig, title=''):
    fig.update_layout(
        title=dict(text=title, font=dict(family='Inter', size=13, color='#1e293b'),
                   x=0, pad=dict(l=4)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248,250,252,1)',
        font=dict(family='Inter', color='#64748b', size=11),
        margin=dict(l=16, r=16, t=44, b=16),
        hoverlabel=dict(bgcolor='#fff', bordercolor='#e2e8f0',
                        font=dict(family='Inter', color='#1e293b')),
        xaxis=dict(gridcolor='#e2e8f0', linecolor='#e2e8f0'),
        yaxis=dict(gridcolor='#e2e8f0', linecolor='#e2e8f0'),
    )
    return fig

def _div(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs=False,
                       config={'displayModeBar': False, 'responsive': True})

def get_analysis_data(db_path):
    con = sqlite3.connect(db_path)
    df_trans = pd.read_sql_query(
        'SELECT platform_id, certificate_id, issue_date, certificate_fee, payment_method FROM Trans', con)
    df_cert = pd.read_sql_query(
        'SELECT id as certificate_id, certificate_name, certificate_type FROM Certificate', con)
    con.close()

    df_trans['issue_date'] = pd.to_datetime(df_trans['issue_date'], errors='coerce')

    rev = (df_trans.groupby('platform_id')['certificate_fee']
           .sum().nlargest(10).reset_index()
           .rename(columns={'platform_id':'Platform','certificate_fee':'Revenue (€)'}))
    rev['Platform'] = 'Plat.' + rev['Platform'].astype(str)
    fig1 = px.bar(rev, x='Platform', y='Revenue (€)', color='Revenue (€)',
                  color_continuous_scale=['#c7d2f8','#334a94'], text='Revenue (€)')
    fig1.update_traces(texttemplate='%{text:.0f}€', textposition='outside', marker_line_width=0)
    fig1.update_coloraxes(showscale=False)
    _dark_layout(fig1, 'Top 10 Platforms by Revenue')

    # Chart 2 — Tipos de certificado
    td = df_cert['certificate_type'].value_counts().reset_index()
    td.columns = ['Type','Count']
    fig2 = px.pie(td, names='Type', values='Count',
                  color_discrete_sequence=COLORS, hole=.55)
    fig2.update_traces(textposition='outside', textinfo='label+percent',
                       textfont=dict(family='Inter', size=11))
    _dark_layout(fig2, 'Certificate Types')

    monthly = (df_trans.dropna(subset=['issue_date'])
               .assign(Month=lambda x: x['issue_date'].dt.to_period('M').astype(str))
               .groupby('Month')['certificate_fee'].sum()
               .reset_index(name='Revenue').sort_values('Month'))
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Revenue'],
                              mode='lines', line=dict(color='#334a94', width=2.5),
                              fill='tozeroy', fillcolor='rgba(51,74,148,.1)',
                              hovertemplate='%{x}<br><b>%{y:,.2f}€</b><extra></extra>'))
    _dark_layout(fig3, 'Monthly Revenue')
    fig3.update_xaxes(nticks=12)

    tc = (df_trans.merge(df_cert, on='certificate_id')
          .groupby('certificate_name').size().nlargest(10)
          .reset_index(name='Count')
          .rename(columns={'certificate_name':'Certificate'}))
    tc['Certificate'] = tc['Certificate'].str[:38]
    tc = tc.sort_values('Count')
    fig4 = px.bar(tc, x='Count', y='Certificate', orientation='h',
                  color='Count', color_continuous_scale=['#c7d2f8','#334a94'], text='Count')
    fig4.update_traces(textposition='outside', marker_line_width=0)
    fig4.update_coloraxes(showscale=False)
    _dark_layout(fig4, 'Top 10 Certificates by Transactions')
    fig4.update_layout(yaxis=dict(tickfont=dict(size=10)))

    pm = df_trans['payment_method'].value_counts().reset_index()
    pm.columns = ['Method','Count']
    fig5 = px.bar(pm, x='Method', y='Count', color='Method',
                  color_discrete_sequence=COLORS, text='Count')
    fig5.update_traces(textposition='outside', marker_line_width=0, showlegend=False)
    _dark_layout(fig5, 'Transactions by Payment Method')

    kpis = {
        'total_revenue':    round(df_trans['certificate_fee'].sum(), 2),
        'avg_fee':          round(df_trans['certificate_fee'].mean(), 2),
        'max_fee':          round(df_trans['certificate_fee'].max(), 2),
        'min_fee':          round(df_trans['certificate_fee'].min(), 2),
        'total_trans':      len(df_trans),
        'active_platforms': int(df_trans['platform_id'].nunique()),
    }

    return {'kpis': kpis,
            'charts': [_div(fig1), _div(fig2), _div(fig3), _div(fig4), _div(fig5)]}
