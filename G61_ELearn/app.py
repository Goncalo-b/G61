
import datetime
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from classes.platform_class import Platform
from classes.certificate import Certificate
from classes.course import Course
from classes.student import Student
from classes.transaction import Trans
from subs.apps_gform import apps_gform
from subs.apps_data_analysis import apps_data_analysis

app = Flask(__name__)
app.secret_key = 'g61_feup_pc2_2026'

db = 'data/novadatabase6.db'
Platform.read(db)
Certificate.read(db)
Course.read(db)
Student.read(db)
Trans.read(db)


def _stats():
    cert_ids = []
    for c in Certificate.obj.values():
        if c._id not in cert_ids:
            cert_ids.append(c._id)

    cert_names = []
    for c in Certificate.obj.values():
        if c._certificate_name and c._certificate_name not in cert_names:
            cert_names.append(c._certificate_name)

    return {
        'platforms':    len(Platform.obj),
        'certificates': len(cert_ids),
        'courses':      len(cert_names),
        'students':     len(Student.obj),
        'transactions': len(Trans.obj),
    }


def _student_by_email(email):
    email_lower = email.lower()
    for s in Student.obj.values():
        if s._student_email.lower() == email_lower:
            return s
    return None


def _unique_certs():
    fees = {}
    for t in Trans.obj.values():
        if t._certificate_id not in fees:
            fees[t._certificate_id] = []
        fees[t._certificate_id].append(t._certificate_fee)

    groups = {}
    for c in Certificate.obj.values():
        name  = c._certificate_name
        ctype = c._certificate_type
        if not name or name in ('None', 'none') or not name.strip():
            continue
        if not ctype or ctype in ('None', 'none') or not ctype.strip():
            continue
        key = (name, ctype)
        if key not in groups:
            groups[key] = {'min_id': c._id, 'fees': []}
        if c._id < groups[key]['min_id']:
            groups[key]['min_id'] = c._id
        if c._id in fees:
            for f in fees[c._id]:
                groups[key]['fees'].append(f)

    out = []
    for (name, ctype), g in groups.items():
        if len(g['fees']) > 0:
            avg_fee = round(sum(g['fees']) / len(g['fees']), 2)
        else:
            avg_fee = 0.0
        if avg_fee <= 0:
            continue
        out.append({'id': g['min_id'], 'name': name, 'type': ctype, 'avg_fee': avg_fee})

    out.sort(key=lambda r: r['name'])
    return out


@app.context_processor
def _inject():
    return {'role': session.get('role', '')}


def _avg_fee_for_cert_name(cert_name):
    cert_ids = []
    for c in Certificate.obj.values():
        if c._certificate_name == cert_name:
            cert_ids.append(c._id)

    if not cert_ids:
        return 0.0

    fees = []
    for t in Trans.obj.values():
        if t._certificate_id in cert_ids:
            fees.append(t._certificate_fee)

    if fees:
        return round(sum(fees) / len(fees), 2)
    return 0.0


def _languages_for_cert_name(cert_name):
    langs = []
    for c in Certificate.obj.values():
        if c._certificate_name == cert_name and c._certificate_language:
            if c._certificate_language not in langs:
                langs.append(c._certificate_language)
    langs.sort()
    return langs


@app.route('/api/students')
def api_students():
    q    = request.args.get('q', '').strip().lower()
    mode = request.args.get('mode', 'contains')
    if not q:
        return jsonify([])
    results = []
    for s in Student.obj.values():
        name_lo = s._student_name.lower()
        match = False
        if mode == 'prefix':
            if name_lo.startswith(q):
                match = True
        else:
            if q in name_lo:
                match = True
            elif q in str(s._id):
                match = True
            elif q in s._student_email.lower():
                match = True
        if match:
            results.append({'id': s._id, 'name': s._student_name,
                            'email': s._student_email, 'country': s._student_country})
            if len(results) >= 12:
                break
    return jsonify(results)


@app.route('/api/student_by_id')
def api_student_by_id():
    try:
        sid = int(request.args.get('id', '0'))
    except ValueError:
        return jsonify(None)
    s = Student.obj.get(sid)
    if s is None:
        return jsonify(None)
    return jsonify({'id': s._id, 'name': s._student_name,
                    'email': s._student_email, 'country': s._student_country})


@app.route('/api/platforms_for_course')
def api_platforms_for_course():
    name = request.args.get('name', '').strip()
    if not name:
        return jsonify([])

    cert_ids = []
    for c in Certificate.obj.values():
        if c._certificate_name == name:
            cert_ids.append(c._id)

    plat_ids = []
    for t in Trans.obj.values():
        if t._certificate_id in cert_ids:
            if t._platform_id not in plat_ids:
                plat_ids.append(t._platform_id)

    plats = []
    for pid in plat_ids:
        if pid in Platform.obj:
            plats.append(Platform.obj[pid])

    plats.sort(key=lambda p: p._platform_name)

    result = []
    for p in plats:
        result.append({'id': p._id, 'name': p._platform_name, 'country': p._platform_country})
    return jsonify(result)


@app.route('/api/languages_for_cert')
def api_languages_for_cert():
    name = request.args.get('name', '').strip()
    if not name:
        return jsonify([])
    return jsonify(_languages_for_cert_name(name))


@app.route('/')
def index():
    student       = None
    student_stats = None
    if session.get('role') == 'student':
        sid     = session.get('student_id')
        student = Student.obj.get(sid)

        my_trans = []
        for t in Trans.obj.values():
            if t._student_id == sid:
                my_trans.append(t)

        my_certs = []
        for t in my_trans:
            if t._certificate_id not in my_certs:
                my_certs.append(t._certificate_id)

        cert_names = []
        for c in Certificate.obj.values():
            if c._certificate_name and c._certificate_name not in cert_names:
                cert_names.append(c._certificate_name)

        cert_types = []
        for c in Certificate.obj.values():
            if c._certificate_type and c._certificate_type not in cert_types:
                cert_types.append(c._certificate_type)

        student_stats = {
            'courses':    len(cert_names),
            'platforms':  len(Platform.obj),
            'cert_types': len(cert_types),
            'my_certs':   len(my_certs),
        }
    return render_template('index.html', ulogin=session.get('user'),
                           stats=_stats(), student=student,
                           student_stats=student_stats)


@app.route('/login')
def login():
    return render_template('login.html', ulogin=None, resul='')


@app.route('/logoff')
def logoff():
    session.clear()
    return redirect(url_for('index'))


@app.route('/chklogin', methods=['post', 'get'])
def chklogin():
    user = request.form.get('user', '')
    pwd  = request.form.get('password', '')

    if (user == 'root' and pwd == '1234') or (user == 'g61' and pwd == 'feup2026'):
        session.update(user=user, role='admin')
        return redirect(url_for('index'))

    s = _student_by_email(user)
    if s and str(s._id) == pwd:
        session.update(user=s._student_name, role='student',
                       student_id=s._id, student_email=s._student_email)
        return redirect(url_for('index'))

    return render_template('login.html', ulogin=None,
                           resul='Utilizador ou password incorretos.')


@app.route('/register', methods=['get', 'post'])
def register():
    if session.get('user'):
        return redirect(url_for('index'))
    msg    = ''
    new_id = Student.get_id(0)

    if request.method == 'POST':
        name    = request.form.get('student_name',    '').strip()
        email   = request.form.get('student_email',   '').strip()
        country = request.form.get('student_country', '').strip()
        try:
            age = int(request.form.get('student_age', 0) or 0)
        except Exception:
            age = 0

        if not name or not email:
            msg = 'err:Nome e email são obrigatórios.'
        elif '@' not in email or '.' not in email.split('@')[-1]:
            msg = 'err:Email inválido.'
        elif age < 0 or age > 120:
            msg = 'err:Idade inválida.'
        elif _student_by_email(email):
            msg = 'err:Já existe uma conta com esse email.'
        else:
            ns = Student(0, name, email, country, age)
            Student.insert(ns._id)
            session.update(user=ns._student_name, role='student',
                           student_id=ns._id, student_email=ns._student_email)
            return redirect(url_for('index'))

    return render_template('register.html', ulogin=None, msg=msg, new_id=new_id)


@app.route('/gform/<cname>', methods=['post', 'get'])
def gform(cname):
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    return apps_gform(cname)


@app.route('/data_analysis', methods=['get', 'post'])
def data_analysis():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    return apps_data_analysis()


@app.route('/analysis')
def analysis(): return redirect(url_for('data_analysis'))

@app.route('/stats')
def stats(): return redirect(url_for('data_analysis'))


@app.route('/history')
def history():
    if not session.get('user'):
        return redirect(url_for('login'))
    role = session.get('role')

    if role == 'admin':
        sid     = request.args.get('student_id', type=int)
        student = None
        if sid:
            student = Student.obj.get(sid)
        trans = []
        if sid:
            for t in Trans.obj.values():
                if t._student_id == sid:
                    trans.append(t)
            trans.sort(key=lambda t: t.issue_date, reverse=True)
        return render_template('history.html', ulogin=session.get('user'),
                               student=student, transactions=trans,
                               platforms=Platform.obj, certificates=Certificate._by_id,
                               selected_sid=sid or '')
    else:
        sid     = session.get('student_id')
        student = Student.obj.get(sid)
        trans   = []
        for t in Trans.obj.values():
            if t._student_id == sid:
                trans.append(t)
        trans.sort(key=lambda t: t.issue_date, reverse=True)
        return render_template('history.html', ulogin=session.get('user'),
                               student=student, transactions=trans,
                               platforms=Platform.obj, certificates=Certificate._by_id,
                               selected_sid='')


@app.route('/enroll', methods=['get', 'post'])
def enroll():
    if not session.get('user'):
        return redirect(url_for('login'))
    role       = session.get('role')
    student_id = session.get('student_id')
    msg        = ''

    if request.method == 'POST':
        mode           = request.form.get('enroll_mode', 'existing')
        platform_id    = int(request.form.get('platform_id',    0) or 0)
        certificate_id = int(request.form.get('certificate_id', 0) or 0)
        payment_method = request.form.get('payment_method', 'Credit Card')
        cert_language  = request.form.get('cert_language', '').strip()

        if role == 'admin':
            if mode == 'new':
                nm = request.form.get('new_name',    '').strip()
                em = request.form.get('new_email',   '').strip()
                ct = request.form.get('new_country', '').strip()
                try:
                    ag = int(request.form.get('new_age', 0) or 0)
                except:
                    ag = 0
                if not nm or not em:
                    msg = 'err:Nome e email são obrigatórios.'
                elif _student_by_email(em):
                    msg = 'err:Já existe um estudante com esse email.'
                else:
                    ns = Student(0, nm, em, ct, ag)
                    Student.insert(ns._id)
                    student_id = ns._id
            else:
                student_id = int(request.form.get('student_id', 0) or 0)

        if not msg.startswith('err'):
            if platform_id and certificate_id and student_id:
                from classes.certificate import Certificate as Cert
                ref_cert = Cert.get_by_id(certificate_id)
                if ref_cert:
                    cert_name = ref_cert._certificate_name
                    cert_type = ref_cert._certificate_type
                else:
                    cert_name = ''
                    cert_type = ''

                hist_langs = _languages_for_cert_name(cert_name)
                if cert_language and cert_language in hist_langs:
                    cert_lang = cert_language
                else:
                    if ref_cert:
                        cert_lang = ref_cert._certificate_language
                    else:
                        cert_lang = ''

                base_fee = _avg_fee_for_cert_name(cert_name)
                if payment_method == 'PayPal':
                    fee = round(base_fee + 1.0, 2)
                else:
                    fee = round(base_fee, 2)

                if fee <= 0 or not cert_name:
                    msg = 'err:Não foi possível determinar a fee do curso.'
                else:
                    try:
                        today = datetime.date.today().isoformat()
                        nc = Cert(0, cert_name, cert_type, cert_lang, today)
                        Cert.insert(nc.get_key())
                        nt = Trans(0, platform_id, nc._id, student_id, fee, payment_method)
                        Trans.insert(nt._id)
                        if payment_method == 'PayPal':
                            surcharge = ' (+€1,00 PayPal)'
                        else:
                            surcharge = ''
                        msg = ('ok:Inscrição confirmada! ID da transação: ' + str(nt._id) +
                               ' · Certificado emitido em ' + today +
                               ' · Fee: €' + f'{fee:.2f}' + surcharge)
                    except Exception as e:
                        msg = 'err:Erro ao registar: ' + str(e)
            elif not msg:
                msg = 'err:Preencha todos os campos obrigatórios.'

    unique_certs = _unique_certs()

    plats_sorted = []
    for p in Platform.obj.values():
        plats_sorted.append(p)
    plats_sorted.sort(key=lambda p: p._platform_name)

    return render_template('enroll.html', ulogin=session.get('user'),
                           student_id=student_id,
                           platforms=plats_sorted,
                           unique_certs=unique_certs,
                           payment_methods=['Credit Card', 'PayPal',
                                            'Bank Transfer', 'Debit Card'],
                           msg=msg)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
