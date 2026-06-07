import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from flask import render_template, session, request

from classes.platform_class import Platform
from classes.certificate import Certificate
from classes.course import Course
from classes.student import Student
from classes.transaction import Trans

COLORS = ['#334a94','#4f6dd4','#10b981','#f59e0b','#ef4444',
          '#06b6d4','#84cc16','#a855f7','#f97316','#14b8a6']

ANALYSIS_OPTIONS = [
    {'value': 'platform_revenue',    'label': '🏆 Top N Plataformas por Receita'},
    {'value': 'platform_trans',      'label': '🔄 Top N Plataformas por Transações'},
    {'value': 'platform_efficiency', 'label': '⚡ Top N Plataformas por Fee Média'},
    {'value': 'top_certs',           'label': '📜 Top N Certificados Mais Emitidos'},
    {'value': 'top_students',        'label': '💰 Top N Estudantes por Gasto Total'},
    {'value': 'top_active_students', 'label': '🔥 Top N Estudantes Mais Ativos'},
    {'value': 'revenue_year',        'label': '📅 Top N Anos por Receita'},
    {'value': 'revenue_month',       'label': '📈 Top N Meses por Receita'},
    {'value': 'payment_method',      'label': '💳 Receita por Método de Pagamento'},
    {'value': 'students_country',    'label': '🌍 Top N Países por Estudantes'},
    {'value': 'age_distribution',    'label': '👥 Distribuição de Idades dos Estudantes'},
    {'value': 'cert_types',          'label': '📊 Tipos de Certificado'},
    {'value': 'courses_category',    'label': '📚 Cursos por Categoria'},
    {'value': 'statistics',          'label': '📋 Estatísticas Gerais'},
]
TOP_N_OPTIONS = [5, 10, 20]

def _layout(fig, title=''):
    fig.update_layout(
        title=dict(text=title, font=dict(family='Inter', size=14, color='#1e293b'),
                   x=0, pad=dict(l=4)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248,250,252,1)',
        font=dict(family='Inter', color='#64748b', size=11),
        margin=dict(l=16, r=16, t=52, b=16),
        hoverlabel=dict(bgcolor='#fff', bordercolor='#e2e8f0',
                        font=dict(family='Inter', color='#1e293b')),
        xaxis=dict(gridcolor='#e2e8f0', linecolor='#e2e8f0'),
        yaxis=dict(gridcolor='#e2e8f0', linecolor='#e2e8f0'),
        height=420,
    )
    return fig

def _div(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn',
                       config={'displayModeBar': False, 'responsive': True})

def _trans_df():

    plats = Platform.obj
    certs = Certificate._by_id
    studs = Student.obj
    rows = []
    for t in Trans.obj.values():
        p = plats.get(t._platform_id)
        c = certs.get(t._certificate_id)
        s = studs.get(t._student_id)
        rows.append({
            'trans_id':             t._id,
            'platform_id':          t._platform_id,
            'platform_name':        p._platform_name if p else None,
            'platform_country':     p._platform_country if p else None,
            'certificate_id':       t._certificate_id,
            'certificate_name':     c._certificate_name if c else None,
            'certificate_type':     c._certificate_type if c else None,
            'certificate_language': c._certificate_language if c else None,
            'issue_date':           str(c._issue_date) if (c and c._issue_date) else None,
            'student_id':           t._student_id,
            'student_name':         s._student_name if s else None,
            'student_country':      s._student_country if s else None,
            'student_age':          s._student_age if s else None,
            'certificate_fee':      float(t._certificate_fee),
            'payment_method':       t._payment_method,
        })
    return pd.DataFrame(rows)

def _student_df():
    rows = [{'id': s._id, 'student_name': s._student_name,
             'student_country': s._student_country, 'student_age': s._student_age}
            for s in Student.obj.values()]
    return pd.DataFrame(rows)

def _certificate_df():
    rows = [{'id': c._id, 'certificate_name': c._certificate_name,
             'certificate_type': c._certificate_type,
             'certificate_language': c._certificate_language,
             'issue_date': str(c._issue_date) if c._issue_date else None}
            for c in Certificate.obj.values()]
    return pd.DataFrame(rows)

def _course_df():
    rows = [{'id': c._id, 'course_name': c._course_name,
             'course_category': c._course_category}
            for c in Course.obj.values()]
    return pd.DataFrame(rows)

def get_stats_html():
    tdf = _trans_df()
    sdf = _student_df()
    cdf = _certificate_df()
    codf = _course_df()

    fees = tdf['certificate_fee']
    total_rev   = round(float(fees.sum()), 2)
    avg_fee     = round(float(fees.mean()), 2)
    max_fee     = round(float(fees.max()), 2)
    min_fee     = round(float(fees.min()), 2)
    total_trans = len(fees)

    active_pl  = int(tdf['platform_id'].nunique())
    total_st   = int(len(sdf))
    total_co   = int(len(codf))
    total_cert = int(cdf['certificate_name'].dropna().nunique())

    pay_counts = tdf['payment_method'].value_counts()
    top_pay_name, top_pay_count = pay_counts.index[0], int(pay_counts.iloc[0])

    co_counts = sdf['student_country'].value_counts()
    top_country_name, top_country_count = co_counts.index[0], int(co_counts.iloc[0])

    cert_counts = cdf['certificate_name'].dropna().value_counts()
    top_cert_name, top_cert_count = cert_counts.index[0], int(cert_counts.iloc[0])

    plat_rev = (tdf.groupby('platform_name')['certificate_fee'].sum()
                   .sort_values(ascending=False))
    top_pl_name = plat_rev.index[0]
    top_pl_rev  = round(float(plat_rev.iloc[0]), 2)

    if tdf['issue_date'].notna().any():
        year_rev = (tdf.dropna(subset=['issue_date'])
                       .assign(ano=lambda d: d['issue_date'].str[:4])
                       .groupby('ano')['certificate_fee'].sum()
                       .sort_values(ascending=False))
        top_year_val = year_rev.index[0]
        top_year_rev = round(float(year_rev.iloc[0]), 2)
    else:
        top_year_val, top_year_rev = '-', 0.0

    sections = [
        ('Finanças', [
            ('Receita Total',  f'{total_rev:,.2f} €'),
            ('Fee Média',      f'{avg_fee:,.2f} €'),
            ('Fee Máxima',     f'{max_fee:,.2f} €'),
            ('Fee Mínima',     f'{min_fee:,.2f} €'),
        ]),
        ('Volume', [
            ('Total de Transações',  f'{total_trans:,}'),
            ('Total de Estudantes',  f'{total_st:,}'),
            ('Plataformas Ativas',   f'{active_pl:,}'),
            ('Total de Cursos',      f'{total_co:,}'),
            ('Tipos de Certificado', f'{total_cert:,}'),
        ]),
        ('Destaques', [
            ('Método de Pagamento Mais Usado',  f'{top_pay_name} ({top_pay_count:,} transações)'),
            ('País com Mais Estudantes',        f'{top_country_name} ({top_country_count:,} estudantes)'),
            ('Certificado Mais Emitido',        f'{top_cert_name} ({top_cert_count:,}×)'),
            ('Plataforma com Maior Receita',    f'{top_pl_name} ({top_pl_rev:,.2f} €)'),
            ('Ano com Maior Receita',           f'{top_year_val} ({top_year_rev:,.2f} €)'),
        ]),
    ]

    html = '<table class="st-table">'
    for sec_title, rows in sections:
        html += f'<tr class="st-sec-hdr"><td colspan="2">{sec_title}</td></tr>'
        for label, value in rows:
            html += f'<tr><td class="st-lbl">{label}</td><td class="st-val">{value}</td></tr>'
    html += '</table>'
    return html

def run_analysis(atype, top_n):
    fig = None; df_display = None; title = ''

    if atype == 'platform_revenue':
        df = (_trans_df().groupby('platform_name', as_index=False)
                          .agg(**{'Receita (€)': ('certificate_fee', 'sum'),
                                  'Transações':  ('trans_id', 'count')})
                          .rename(columns={'platform_name': 'Plataforma'})
                          .sort_values('Receita (€)', ascending=False)
                          .head(top_n).reset_index(drop=True))
        df['Receita (€)'] = df['Receita (€)'].round(2)
        fig = px.bar(df, x='Plataforma', y='Receita (€)', color='Receita (€)',
                     color_continuous_scale=['#c7d2f8','#334a94'], text='Receita (€)')
        fig.update_traces(texttemplate='%{text:.0f}€', textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        title = f'Top {top_n} Plataformas por Receita'
        df_display = df

    elif atype == 'platform_trans':
        df = (_trans_df().groupby('platform_name', as_index=False)
                          .agg(**{'Transações':  ('trans_id', 'count'),
                                  'Receita (€)': ('certificate_fee', 'sum')})
                          .rename(columns={'platform_name': 'Plataforma'})
                          .sort_values('Transações', ascending=False)
                          .head(top_n).reset_index(drop=True))
        df['Receita (€)'] = df['Receita (€)'].round(2)
        fig = px.bar(df, x='Plataforma', y='Transações', color='Transações',
                     color_continuous_scale=['#c7d2f8','#334a94'], text='Transações')
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        title = f'Top {top_n} Plataformas por Nº de Transações'
        df_display = df

    elif atype == 'platform_efficiency':
        agg = (_trans_df().groupby('platform_name', as_index=False)
                           .agg(**{'Fee Média (€)':       ('certificate_fee', 'mean'),
                                   'Transações':         ('trans_id', 'count'),
                                   'Receita Total (€)':  ('certificate_fee', 'sum')}))
        df = (agg[agg['Transações'] >= 5]
                .rename(columns={'platform_name': 'Plataforma'})
                .sort_values('Fee Média (€)', ascending=False)
                .head(top_n).reset_index(drop=True))
        df['Fee Média (€)']      = df['Fee Média (€)'].round(2)
        df['Receita Total (€)']  = df['Receita Total (€)'].round(2)
        fig = px.bar(df, x='Plataforma', y='Fee Média (€)', color='Fee Média (€)',
                     color_continuous_scale=['#c7d2f8','#334a94'],
                     hover_data=['Transações','Receita Total (€)'], text='Fee Média (€)')
        fig.update_traces(texttemplate='%{text:.2f}€', textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        title = f'Top {top_n} Plataformas por Fee Média'
        df_display = df

    elif atype == 'top_certs':
        tdf = _trans_df().dropna(subset=['certificate_name'])
        df = (tdf.groupby('certificate_name', as_index=False)
                  .agg(Tipo=('certificate_type','first'),
                       **{'Emissões': ('trans_id','count'),
                          'Fee Média (€)': ('certificate_fee','mean')})
                  .rename(columns={'certificate_name':'Certificado'})
                  .sort_values('Emissões', ascending=False)
                  .head(top_n).reset_index(drop=True))
        df['Certificado']    = df['Certificado'].str[:45]
        df['Fee Média (€)']  = df['Fee Média (€)'].round(2)
        df_s = df.sort_values('Emissões')
        fig = px.bar(df_s, x='Emissões', y='Certificado', orientation='h',
                     color='Emissões', color_continuous_scale=['#c7d2f8','#334a94'], text='Emissões')
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(height=max(380, top_n * 38 + 80),
                          yaxis=dict(tickfont=dict(size=10)))
        title = f'Top {top_n} Certificados por Emissões'
        df_display = df

    elif atype == 'top_students':
        df = (_trans_df().groupby('student_name', as_index=False)
                          .agg(País=('student_country','first'),
                               **{'Total Gasto (€)': ('certificate_fee','sum'),
                                  'Transações':     ('trans_id','count')})
                          .rename(columns={'student_name':'Estudante'})
                          .sort_values('Total Gasto (€)', ascending=False)
                          .head(top_n).reset_index(drop=True))
        df['Total Gasto (€)'] = df['Total Gasto (€)'].round(2)
        fig = px.bar(df, x='Estudante', y='Total Gasto (€)', color='Total Gasto (€)',
                     color_continuous_scale=['#c7d2f8','#334a94'],
                     hover_data=['País','Transações'], text='Total Gasto (€)')
        fig.update_traces(texttemplate='%{text:.2f}€', textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        title = f'Top {top_n} Estudantes por Gasto Total'
        df_display = df

    elif atype == 'top_active_students':
        df = (_trans_df().groupby('student_name', as_index=False)
                          .agg(País=('student_country','first'),
                               **{'Transações':     ('trans_id','count'),
                                  'Total Gasto (€)':('certificate_fee','sum')})
                          .rename(columns={'student_name':'Estudante'})
                          .sort_values('Transações', ascending=False)
                          .head(top_n).reset_index(drop=True))
        df['Total Gasto (€)'] = df['Total Gasto (€)'].round(2)
        fig = px.bar(df, x='Estudante', y='Transações', color='Transações',
                     color_continuous_scale=['#c7d2f8','#334a94'],
                     hover_data=['País','Total Gasto (€)'], text='Transações')
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        title = f'Top {top_n} Estudantes Mais Ativos (por Nº de Transações)'
        df_display = df

    elif atype == 'revenue_year':
        tdf = _trans_df().dropna(subset=['issue_date'])
        tdf = tdf.assign(Ano=tdf['issue_date'].str[:4])
        df = (tdf.groupby('Ano', as_index=False)
                  .agg(**{'Receita (€)': ('certificate_fee','sum'),
                          'Transações':  ('trans_id','count')})
                  .sort_values('Receita (€)', ascending=False)
                  .head(top_n)
                  .sort_values('Ano').reset_index(drop=True))
        df['Receita (€)'] = df['Receita (€)'].round(2)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Ano'], y=df['Receita (€)'], marker_color=COLORS[0],
                             text=df['Receita (€)'], texttemplate='%{text:.0f}€',
                             textposition='outside',
                             hovertemplate='%{x}<br><b>%{y:,.2f}€</b><extra></extra>'))
        title = f'Top {top_n} Anos por Receita'
        df_display = df

    elif atype == 'revenue_month':
        tdf = _trans_df().dropna(subset=['issue_date'])
        tdf = tdf.assign(Mês=tdf['issue_date'].str[:7])
        df = (tdf.groupby('Mês', as_index=False)
                  .agg(**{'Receita (€)': ('certificate_fee','sum'),
                          'Transações':  ('trans_id','count')})
                  .sort_values('Receita (€)', ascending=False)
                  .head(top_n)
                  .sort_values('Mês').reset_index(drop=True))
        df['Receita (€)'] = df['Receita (€)'].round(2)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Mês'], y=df['Receita (€)'], mode='lines+markers',
            line=dict(color=COLORS[0], width=2),
            marker=dict(size=5, color=COLORS[0]),
            fill='tozeroy', fillcolor='rgba(51,74,148,.08)',
            hovertemplate='%{x}<br><b>%{y:,.2f}€</b><extra></extra>'))
        fig.update_layout(height=380)
        title = f'Top {top_n} Meses por Receita'
        df_display = df

    elif atype == 'payment_method':
        df = (_trans_df().groupby('payment_method', as_index=False)
                          .agg(**{'Transações':   ('trans_id','count'),
                                  'Receita (€)':  ('certificate_fee','sum'),
                                  'Fee Média (€)':('certificate_fee','mean')})
                          .rename(columns={'payment_method':'Método'})
                          .sort_values('Transações', ascending=False).reset_index(drop=True))
        df['Receita (€)']   = df['Receita (€)'].round(2)
        df['Fee Média (€)'] = df['Fee Média (€)'].round(2)
        fig = px.pie(df, names='Método', values='Receita (€)',
                     color_discrete_sequence=COLORS, hole=0.52)
        fig.update_traces(textposition='outside', textinfo='label+percent',
                          textfont=dict(family='Inter', size=11))
        title = 'Receita por Método de Pagamento'
        df_display = df

    elif atype == 'students_country':
        df = (_student_df().groupby('student_country', as_index=False)
                            .agg(Estudantes=('id','count'))
                            .rename(columns={'student_country':'País'})
                            .sort_values('Estudantes', ascending=False)
                            .head(top_n).reset_index(drop=True))
        fig = px.bar(df, x='País', y='Estudantes', color='Estudantes',
                     color_continuous_scale=['#c7d2f8','#334a94'], text='Estudantes')
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        title = f'Top {top_n} Países por Nº de Estudantes'
        df_display = df

    elif atype == 'age_distribution':
        sdf = _student_df()
        bins   = [17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 200]
        labels = ['18–22', '23–27', '28–32', '33–37', '38–42',
                  '43–47', '48–52', '53–57', '58–62', '63–67', '68+']
        sdf['Grupo'] = pd.cut(sdf['student_age'], bins=bins, labels=labels)
        agg = sdf.groupby('Grupo', observed=True).size().reset_index(name='Estudantes')
        fig = px.bar(agg, x='Grupo', y='Estudantes', color='Estudantes',
                     color_continuous_scale=['#c7d2f8','#334a94'], text='Estudantes')
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        title = 'Distribuição de Idades dos Estudantes (Grupos de 5 Anos)'
        df_display = agg

    elif atype == 'cert_types':
        df = (_certificate_df().groupby('certificate_type', as_index=False)
                                .agg(Certificados=('id','count'))
                                .rename(columns={'certificate_type':'Tipo'})
                                .sort_values('Certificados', ascending=False).reset_index(drop=True))
        fig = px.pie(df, names='Tipo', values='Certificados',
                     color_discrete_sequence=COLORS, hole=0.52)
        fig.update_traces(textposition='outside', textinfo='label+percent+value',
                          textfont=dict(family='Inter', size=11))
        title = 'Tipos de Certificado'
        df_display = df

    elif atype == 'courses_category':
        df = (_course_df().groupby('course_category', as_index=False)
                           .agg(Cursos=('id','count'))
                           .rename(columns={'course_category':'Categoria'})
                           .sort_values('Cursos', ascending=False).reset_index(drop=True))
        df_s = df.sort_values('Cursos')
        fig = px.bar(df_s, x='Cursos', y='Categoria', orientation='h',
                     color='Cursos', color_continuous_scale=['#c7d2f8','#334a94'], text='Cursos')
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        title = 'Cursos por Categoria'
        df_display = df

    else:
        return '', '', '', None

    _layout(fig, title)
    return (_div(fig),
            df_display.to_html(classes='stats-table pd-table', index=False, border=0),
            title, df_display)

def apps_data_analysis():
    ulogin = session.get('user')

    atype = (request.form.get('analysis_type') or
             request.args.get('type') or 'platform_revenue')
    try:
        top_n = int(request.form.get('top_n') or request.args.get('top_n') or 10)
    except:
        top_n = 10
    if top_n not in TOP_N_OPTIONS:
        top_n = 10

    if atype == 'statistics':
        return render_template('data_analysis.html',
                               ulogin=ulogin,
                               stats_html=get_stats_html(),
                               chart_html=None, table_html=None, chart_title=None,
                               analysis_options=ANALYSIS_OPTIONS,
                               top_n_options=TOP_N_OPTIONS,
                               selected_type=atype, selected_n=top_n)

    chart_html, table_html, chart_title, _ = run_analysis(atype, top_n)

    return render_template('data_analysis.html',
                           ulogin=ulogin,
                           stats_html=None,
                           chart_html=chart_html, table_html=table_html,
                           chart_title=chart_title,
                           analysis_options=ANALYSIS_OPTIONS,
                           top_n_options=TOP_N_OPTIONS,
                           selected_type=atype, selected_n=top_n)
