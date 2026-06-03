"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Trans
"""
import datetime
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

    def __str__(self):
        return f'Id:{self._id}, Date:{self._issue_date}, Fee:{self._certificate_fee:.2f}'
