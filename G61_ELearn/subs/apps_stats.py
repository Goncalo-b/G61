from flask import render_template, session
from classes.platform_class import Platform
from classes.certificate import Certificate
from classes.course import Course
from classes.person import Person
from classes.transaction import Trans

def apps_stats():
    ulogin = session.get("user")
    if ulogin is None:
        from subs.apps_gform import get_stats
        return render_template("index.html", ulogin=None, stats=get_stats())

    data = {
        'total_revenue':    Trans.total_revenue(),
        'avg_fee':          Trans.average_fee(),
        'max_fee':          Trans.max_fee(),
        'min_fee':          Trans.min_fee(),
        'total_trans':      len(Trans.obj),
        'total_platforms':  len(Platform.obj),
        'total_certs':      len(Certificate.obj),
        'total_courses':    len(Course.obj),
        'total_persons':    len(Person.obj),

        'top_platforms_revenue': Platform.revenue_per_platform(Trans.obj, top_n=10),
        'top_platforms_trans':   Platform.transactions_per_platform(Trans.obj, top_n=10),
        'platforms_by_country':  Platform.platforms_per_country(),
        'avg_revenue_platform':  Platform.avg_revenue_per_platform(Trans.obj),

        
        'most_issued':           Certificate.most_issued(Trans.obj, top_n=10),
        'cert_by_type':          Certificate.distribution_by_type(),
        'cert_by_language':      Certificate.distribution_by_language(),
        'avg_fee_by_type':       Certificate.avg_fee_by_type(Trans.obj),

        'courses_by_category':   Course.distribution_by_category(),
        'courses_per_platform':  Course.courses_per_platform(top_n=10),
        'courses_by_year':       Course.courses_added_by_year(),

        'top_spenders':          Person.top_spenders(Trans.obj, top_n=10),
        'most_active':           Person.most_active(Trans.obj, top_n=10),
        'persons_by_country':    Person.distribution_by_country(),
        'age_distribution':      Person.age_distribution(),

        'revenue_by_payment':    Trans.revenue_by_payment_method(),
        'revenue_by_year':       Trans.revenue_by_year(),
    }

    return render_template("stats.html", ulogin=ulogin, d=data)
