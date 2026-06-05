from flask import render_template, request, session
from classes.platform_class import Platform
from classes.certificate import Certificate
from classes.course import Course
from classes.person import Person
from classes.transaction import Trans

prev_option  = ""
filter_active = {}

def get_stats():
    return {
        'platforms':    len(Platform.obj),
        'certificates': len(Certificate.obj),
        'courses':      len(Course.obj),
        'persons':      len(Person.obj),
        'transactions': len(Trans.obj),
    }

def apply_filter(cl, filters):
    """Filtra cl.lst por substring em qualquer campo."""
    active = {k: v for k, v in filters.items() if v.strip()}
    if not active:
        cl.lst = list(cl.obj.keys())
        cl.pos = 0
        return False
    matching = []
    for obj in cl.obj.values():
        ok = True
        for att, val in active.items():
            obj_val = str(getattr(obj, att)).lower()
            if val.lower() not in obj_val:
                ok = False
                break
        if ok:
            pk = getattr(obj, cl.att[0])
            matching.append(pk)
    cl.lst = matching
    cl.pos  = 0
    return True

def apps_gform(cname=''):
    global prev_option, filter_active
    ulogin = session.get("user")
    if ulogin is None:
        return render_template("index.html", ulogin=None, stats=get_stats())

    cl      = eval(cname)
    butshow = "enabled"
    butedit = "disabled"
    option  = request.args.get("option", "")
    msg     = ""
    total_unfiltered = len(cl.obj)


    cur_filter = filter_active.get(cname, {})

    if option == "filter":
        filters = {}
        for att in cl.att[1:]:   # ignora _id
            val = request.form.get("f_" + att, "")
            filters[att] = val
        is_filtered = apply_filter(cl, filters)
        filter_active[cname] = filters if is_filtered else {}
        cur_filter = filter_active[cname]
        if is_filtered:
            msg = f"ok:Filtro aplicado — {len(cl.lst)} registo(s) encontrado(s)."
        else:
            msg = "ok:Filtro removido — a mostrar todos os registos."

    elif option == "clearfilter":
        filter_active[cname] = {}
        cur_filter = {}
        cl.lst = list(cl.obj.keys())
        cl.pos = 0
        msg = "ok:Filtro removido."

    elif prev_option == 'insert' and option == 'save':
        try:
            strobj = request.form.get(cl.att[0], '0')
            for i in range(1, len(cl.att)):
                strobj += ";" + request.form.get(cl.att[i], '')
            obj = cl.from_string(strobj)
            cl.insert(getattr(obj, cl.att[0]))
            cl.lst = list(cl.obj.keys())   
            filter_active[cname] = {}
            cl.last()
            msg = "ok:Registo inserido com sucesso."
        except Exception as e:
            msg = f"err:Erro ao inserir: {e}"

    elif prev_option == 'edit' and option == 'save':
        try:
            obj = cl.current()
            for i in range(1, len(cl.att)):
                setattr(obj, cl.att[i], request.form.get(cl.att[i], ''))
            cl.update(getattr(obj, cl.att[0]))
            msg = "ok:Registo atualizado com sucesso."
        except Exception as e:
            msg = f"err:Erro ao atualizar: {e}"

    else:
        if option == "edit":
            butshow, butedit = "disabled", "enabled"
        elif option == "delete":
            try:
                obj = cl.current()
                cl.remove(obj.id)
                if not cl.previous():
                    cl.first()
                msg = "ok:Registo eliminado."
            except Exception as e:
                msg = f"err:Erro ao eliminar: {e}"
        elif option == "insert":
            butshow, butedit = "disabled", "enabled"
        elif option == "goto":
            try:
                sid = int(request.args.get("search_id", 0))
                if sid in cl.obj:
                    cl.current(sid)
                else:
                    msg = "err:ID não encontrado."
            except:
                msg = "err:ID inválido."
        elif option in ("first", "previous", "next", "last", "cancel"):
            if   option == "first":    cl.first()
            elif option == "previous": cl.previous()
            elif option == "next":     cl.nextrec()
            elif option == "last":     cl.last()
        elif option == "exit":
            return render_template("index.html", ulogin=ulogin, stats=get_stats())

    prev_option = option
    obj = cl.current()

    if option == 'insert' or len(cl.lst) == 0:
        obj = {cl.att[0]: cl.get_id(0)}
        for i in range(1, len(cl.att)):
            obj[cl.att[i]] = ""

    recnum = (cl.pos + 1) if len(cl.lst) > 0 else 0
    total  = len(cl.lst)
    is_filtered = bool(cur_filter and any(v.strip() for v in cur_filter.values()))

    return render_template("gform.html",
                           butshow=butshow, butedit=butedit,
                           cname=cname, obj=obj,
                           att=cl.att, des=cl.des,
                           header=cl.header,
                           recnum=recnum, total=total,
                           total_unfiltered=total_unfiltered,
                           is_filtered=is_filtered,
                           cur_filter=cur_filter,
                           msg=msg, ulogin=ulogin)
