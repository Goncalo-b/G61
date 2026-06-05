"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Trans
"""
import datetime
from collections import defaultdict, Counter
from classes.gclass import Gclass

class Trans(Gclass):
    obj     = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_platform_id', '_certificate_id', '_person_id',
               '_issue_date', '_certificate_fee', '_payment_method']
    header  = 'Transaction'
    des     = ['Id', 'Platform Id', 'Certificate Id', 'Person Id',
               'Issue Date', 'Fee (€)', 'Payment Method']

    def __init__(self, id, platform_id, certificate_id, person_id,
                 issue_date, certificate_fee, payment_method=''):
        super().__init__()
        id = Trans.get_id(int(float(id)))
        self._id              = id
        self._platform_id     = int(float(platform_id))
        self._certificate_id  = int(float(certificate_id))
        self._person_id       = int(float(person_id))
        self._certificate_fee = float(certificate_fee)
        self._payment_method  = str(payment_method)
        if isinstance(issue_date, str):
            self._issue_date = datetime.date.fromisoformat(str(issue_date)[:10])
        else:
            self._issue_date = issue_date
        Trans.obj[id] = self
        Trans.lst.append(id)

    @property
    def id(self): return self._id

    @property
    def platform_id(self): return self._platform_id
    @platform_id.setter
    def platform_id(self, v): self._platform_id = int(float(v))

    @property
    def certificate_id(self): return self._certificate_id
    @certificate_id.setter
    def certificate_id(self, v): self._certificate_id = int(float(v))

    @property
    def person_id(self): return self._person_id
    @person_id.setter
    def person_id(self, v): self._person_id = int(float(v))

    @property
    def issue_date(self): return self._issue_date
    @issue_date.setter
    def issue_date(self, v):
        if str(v) != '':
            self._issue_date = datetime.date.fromisoformat(str(v)[:10])

    @property
    def certificate_fee(self): return self._certificate_fee
    @certificate_fee.setter
    def certificate_fee(self, v): self._certificate_fee = float(v)

    @property
    def payment_method(self): return self._payment_method
    @payment_method.setter
    def payment_method(self, v): self._payment_method = str(v)


    @classmethod
    def total_revenue(cls):
        return round(sum(t._certificate_fee for t in cls.obj.values()), 2)

    @classmethod
    def average_fee(cls):
        if not cls.obj: return 0.0
        return round(cls.total_revenue() / len(cls.obj), 2)

    @classmethod
    def max_fee(cls):
        if not cls.obj: return 0.0
        return round(max(t._certificate_fee for t in cls.obj.values()), 2)

    @classmethod
    def min_fee(cls):
        if not cls.obj: return 0.0
        return round(min(t._certificate_fee for t in cls.obj.values()), 2)

    @classmethod
    def revenue_by_payment_method(cls):
        totals = defaultdict(float)
        counts = defaultdict(int)
        for t in cls.obj.values():
            totals[t._payment_method] += t._certificate_fee
            counts[t._payment_method] += 1
        result = []
        for method in totals:
            result.append({
                'method': method,
                'revenue': round(totals[method], 2),
                'count': counts[method],
                'avg': round(totals[method] / counts[method], 2)
            })
        return sorted(result, key=lambda x: x['revenue'], reverse=True)

    @classmethod
    def revenue_by_month(cls):
        totals = defaultdict(float)
        for t in cls.obj.values():
            month = str(t._issue_date)[:7]
            totals[month] += t._certificate_fee
        return [(m, round(v, 2)) for m, v in sorted(totals.items())]

    @classmethod
    def revenue_by_year(cls):
        totals = defaultdict(float)
        counts = defaultdict(int)
        for t in cls.obj.values():
            year = str(t._issue_date)[:4]
            totals[year] += t._certificate_fee
            counts[year] += 1
        result = []
        for year in sorted(totals):
            result.append({'year': year, 'revenue': round(totals[year], 2),
                           'count': counts[year]})
        return result

    @classmethod
    def transactions_per_year(cls):
        counts = Counter(str(t._issue_date)[:4] for t in cls.obj.values())
        return sorted(counts.items())

    def __str__(self):
        return f'Id:{self._id}, Date:{self._issue_date}, Fee:{self._certificate_fee:.2f}'
