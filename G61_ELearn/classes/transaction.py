import datetime
from classes.gclass import Gclass

class Trans(Gclass):
    obj     = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_platform_id', '_certificate_id', '_student_id',
               '_certificate_fee', '_payment_method']
    header  = 'Transaction'
    des     = ['Id', 'Platform Id', 'Certificate Id', 'Student Id',
               'Fee (€)', 'Payment Method']

    def __init__(self, id, platform_id, certificate_id, student_id,
                 certificate_fee, payment_method=''):
        super().__init__()
        id = Trans.get_id(int(float(id)))
        self._id              = id
        self._platform_id     = int(float(platform_id))
        self._certificate_id  = int(float(certificate_id))
        self._student_id      = int(float(student_id))
        self._certificate_fee = float(certificate_fee)
        self._payment_method  = str(payment_method)
        Trans.obj[id] = self
        Trans.lst.append(id)

    @property
    def id(self):
        return self._id

    @property
    def platform_id(self): 
        return self._platform_id
    
    @platform_id.setter
    def platform_id(self, v): 
        self._platform_id = int(float(v))

    @property
    def certificate_id(self):
        return self._certificate_id
    
    @certificate_id.setter
    def certificate_id(self, v): 
        self._certificate_id = int(float(v))

    @property
    def student_id(self): 
        return self._student_id
    
    @student_id.setter
    def student_id(self, v):
        self._student_id = int(float(v))

    @property
    def _person_id(self): 
        return self._student_id
    
    @_person_id.setter
    def _person_id(self, v):
        self._student_id = int(float(v))

    @property
    def issue_date(self):
        from classes.certificate import Certificate
        c = Certificate.get_by_id(self._certificate_id)
        if c:
            return c._issue_date
        return ''

    @property
    def certificate_fee(self): 
        return self._certificate_fee
    
    @certificate_fee.setter
    def certificate_fee(self, v): 
        self._certificate_fee = float(v)

    @property
    def payment_method(self): 
        return self._payment_method
    
    @payment_method.setter
    def payment_method(self, v): 
        self._payment_method = str(v)

    @classmethod
    def total_revenue(cls):
        total = 0.0
        for t in cls.obj.values():
            total += t._certificate_fee
        return round(total, 2)

    @classmethod
    def average_fee(cls):
        if not cls.obj:
            return 0.0
        total = 0.0
        for t in cls.obj.values():
            total += t._certificate_fee
        return round(total / len(cls.obj), 2)

    @classmethod
    def max_fee(cls):
        if not cls.obj:
            return 0.0
        biggest = 0.0
        for t in cls.obj.values():
            if t._certificate_fee > biggest:
                biggest = t._certificate_fee
        return round(biggest, 2)

    @classmethod
    def min_fee(cls):
        if not cls.obj:
            return 0.0
        smallest = None
        for t in cls.obj.values():
            if smallest is None or t._certificate_fee < smallest:
                smallest = t._certificate_fee
        return round(smallest, 2)

    @classmethod
    def revenue_by_payment_method(cls):
        totals = {}
        counts = {}
        for t in cls.obj.values():
            method = t._payment_method
            if method not in totals:
                totals[method] = 0.0
                counts[method] = 0
            totals[method] += t._certificate_fee
            counts[method] += 1

        result = []
        for method in totals:
            avg = round(totals[method] / counts[method], 2)
            result.append({'method': method, 'revenue': round(totals[method], 2),
                           'count': counts[method], 'avg': avg})
        result.sort(key=lambda x: x['revenue'], reverse=True)
        return result

    @classmethod
    def revenue_by_month(cls):
        from classes.certificate import Certificate
        totals = {}
        for t in cls.obj.values():
            c = Certificate.get_by_id(t._certificate_id)
            if c and c._issue_date:
                month = c._issue_date[:7]
                if month not in totals:
                    totals[month] = 0.0
                totals[month] += t._certificate_fee

        result = []
        for month in sorted(totals.keys()):
            result.append((month, round(totals[month], 2)))
        return result

    @classmethod
    def revenue_by_year(cls):
        from classes.certificate import Certificate
        totals = {}
        counts = {}
        for t in cls.obj.values():
            c = Certificate.get_by_id(t._certificate_id)
            if c and c._issue_date:
                year = c._issue_date[:4]
                if year not in totals:
                    totals[year] = 0.0
                    counts[year] = 0
                totals[year] += t._certificate_fee
                counts[year] += 1

        result = []
        for year in sorted(totals.keys()):
            result.append({'year': year, 'revenue': round(totals[year], 2),
                           'count': counts[year]})
        return result

    @classmethod
    def transactions_per_year(cls):
        from classes.certificate import Certificate
        counts = {}
        for t in cls.obj.values():
            c = Certificate.get_by_id(t._certificate_id)
            if c and c._issue_date:
                year = c._issue_date[:4]
                if year not in counts:
                    counts[year] = 0
                counts[year] += 1

        result = []
        for year in sorted(counts.keys()):
            result.append((year, counts[year]))
        return result

    def __str__(self):
        return 'Id:' + str(self._id) + ', Cert:' + str(self._certificate_id) + ', Fee:' + f'{self._certificate_fee:.2f}'
