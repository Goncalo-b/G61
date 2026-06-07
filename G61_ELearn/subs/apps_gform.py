from flask import render_template, request, session
from classes.platform_class import Platform
from classes.certificate import Certificate
from classes.course import Course
from classes.student import Student
from classes.transaction import Trans

_CLASSES = {
    'Platform':    Platform,
    'Certificate': Certificate,
    'Course':      Course,
    'Student':     Student,
    'Trans':       Trans,
}

def get_stats():
    result = {}
    result['platforms']    = len(Platform.obj)
    result['certificates'] = len(Certificate.obj)
    result['courses']      = len(Course.obj)
    result['students']     = len(Student.obj)
    result['transactions'] = len(Trans.obj)
    return result

def apply_filter(cl, filters):
    active = {}
    for k, v in filters.items():
        if v.strip():
            active[k] = v

    if not active:
        cl.lst = list(cl.obj.keys())
        cl.pos = 0
        return False

    matching = []
    for key, obj in cl.obj.items():
        passes = True
        for att, v in active.items():
            field_value = str(getattr(obj, att)).lower()
            if str(v).lower() not in field_value:
                passes = False
                break
        if passes:
            matching.append(key)

    cl.lst = matching
    cl.pos = 0
    return True

def apps_gform(cname=''):
    ulogin = session.get('user')
    if ulogin is None:
        return render_template('index.html', ulogin=None, stats=get_stats(), student=None)

    cl = _CLASSES.get(cname)
    if cl is None:
        return render_template('index.html', ulogin=ulogin, stats=get_stats(), student=None)

    butshow = 'enabled'
    butedit = 'disabled'
    option  = request.args.get('option', '')
    msg     = ''
    total_unfiltered = len(cl.obj)

    prev_option = request.form.get('prev_option', '')

    sess_key   = 'filter_' + cname
    cur_filter = session.get(sess_key, {})

    if option == 'filter':
        filters = {}
        for att in cl.att:
            filters[att] = request.form.get('f_' + att, '')
        is_filtered = apply_filter(cl, filters)
        if is_filtered:
            session[sess_key] = filters
        else:
            session[sess_key] = {}
        cur_filter = session[sess_key]
        if is_filtered:
            msg = 'ok:Filtro aplicado — ' + str(len(cl.lst)) + ' registo(s) encontrado(s).'
        else:
            msg = 'ok:Filtro removido — a mostrar todos os registos.'

    elif option == 'clearfilter':
        session.pop(sess_key, None)
        cur_filter = {}
        cl.lst = list(cl.obj.keys())
        cl.pos = 0
        msg = 'ok:Filtro removido.'

    elif prev_option == 'insert' and option == 'save':
        try:
            strobj = request.form.get(cl.att[0], '0')
            for i in range(1, len(cl.att)):
                strobj += ';' + request.form.get(cl.att[i], '')
            obj = cl.from_string(strobj)
            if hasattr(obj, 'get_key'):
                key = obj.get_key()
            else:
                key = getattr(obj, cl.att[0])
            cl.insert(key)
            cl.lst = list(cl.obj.keys())
            session.pop(sess_key, None)
            cur_filter = {}
            cl.last()
            msg = 'ok:Registo inserido com sucesso.'
        except Exception as e:
            msg = 'err:Erro ao inserir: ' + str(e)

    elif prev_option == 'edit' and option == 'save':
        try:
            obj = cl.current()
            for i in range(1, len(cl.att)):
                setattr(obj, cl.att[i], request.form.get(cl.att[i], ''))
            cl.update(getattr(obj, cl.att[0]))
            msg = 'ok:Registo atualizado com sucesso.'
        except Exception as e:
            msg = 'err:Erro ao atualizar: ' + str(e)

    else:
        if option == 'edit':
            butshow = 'disabled'
            butedit = 'enabled'
        elif option == 'insert':
            butshow = 'disabled'
            butedit = 'enabled'
        elif option == 'delete':
            try:
                obj = cl.current()
                cl.remove(obj.id)
                if not cl.previous():
                    cl.first()
                msg = 'ok:Registo eliminado.'
            except Exception as e:
                msg = 'err:Erro ao eliminar: ' + str(e)
        elif option == 'goto':
            try:
                sid = int(request.args.get('search_id', 0))
                if sid in cl.obj:
                    cl.current(sid)
                    msg = 'ok:Registo ' + str(sid) + ' encontrado.'
                else:
                    msg = 'err:ID não encontrado.'
            except:
                msg = 'err:ID inválido.'
        elif option == 'first':
            cl.first()
        elif option == 'previous':
            cl.previous()
        elif option == 'next':
            cl.nextrec()
        elif option == 'last':
            cl.last()
        elif option == 'cancel':
            pass
        elif option == 'exit':
            return render_template('index.html', ulogin=ulogin,
                                   stats=get_stats(), student=None)

    obj = cl.current()
    if option == 'insert' or len(cl.lst) == 0:
        obj = {cl.att[0]: cl.get_id(0)}
        for i in range(1, len(cl.att)):
            obj[cl.att[i]] = ''

    recnum = 0
    if cl.lst:
        recnum = cl.pos + 1
    total  = len(cl.lst)

    is_filtered = False
    if cur_filter:
        for v in cur_filter.values():
            if v.strip():
                is_filtered = True
                break

    return render_template('gform.html',
                           butshow=butshow, butedit=butedit,
                           cname=cname, obj=obj,
                           att=cl.att, des=cl.des,
                           header=cl.header,
                           recnum=recnum, total=total,
                           total_unfiltered=total_unfiltered,
                           is_filtered=is_filtered,
                           cur_filter=cur_filter,
                           current_option=option,
                           msg=msg, ulogin=ulogin)
