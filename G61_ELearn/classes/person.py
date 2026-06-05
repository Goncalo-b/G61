"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Person
"""
from collections import defaultdict, Counter
from classes.gclass import Gclass

class Person(Gclass):
    obj     = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_person_name', '_person_email', '_person_country', '_person_age']
    header  = 'Person'
    des     = ['Id', 'Name', 'Email', 'Country', 'Age']

    def __init__(self, id, person_name, person_email, person_country='', person_age=0):
        super().__init__()
        id = Person.get_id(int(float(id)))
        self._id             = id
        self._person_name    = str(person_name)
        self._person_email   = str(person_email)
        self._person_country = str(person_country)
        self._person_age     = int(float(person_age)) if str(person_age) != '' else 0
        Person.obj[id] = self
        Person.lst.append(id)

    @property
    def id(self): return self._id

    @property
    def person_name(self): return self._person_name
    @person_name.setter
    def person_name(self, v): self._person_name = str(v)

    @property
    def person_email(self): return self._person_email
    @person_email.setter
    def person_email(self, v): self._person_email = str(v)

    @property
    def person_country(self): return self._person_country
    @person_country.setter
    def person_country(self, v): self._person_country = str(v)

    @property
    def person_age(self): return self._person_age
    @person_age.setter
    def person_age(self, v): self._person_age = int(float(v)) if str(v) != '' else 0


    @classmethod
    def top_spenders(cls, trans_obj, top_n=10):
        """Pessoas que mais gastaram."""
        totals = defaultdict(float)
        for t in trans_obj.values():
            totals[t._person_id] += t._certificate_fee
        ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:top_n]
        result = []
        for pid, total in ranked:
            name = cls.obj[pid].person_name if pid in cls.obj else f'Person {pid}'
            country = cls.obj[pid].person_country if pid in cls.obj else ''
            result.append({'id': pid, 'name': name, 'country': country,
                           'total': round(total, 2)})
        return result

    @classmethod
    def most_active(cls, trans_obj, top_n=10):
        """Pessoas com mais transações."""
        counts = Counter(t._person_id for t in trans_obj.values())
        result = []
        for pid, count in counts.most_common(top_n):
            name = cls.obj[pid].person_name if pid in cls.obj else f'Person {pid}'
            result.append({'id': pid, 'name': name, 'count': count})
        return result

    @classmethod
    def distribution_by_country(cls):
        """Número de persons por país."""
        counts = Counter(p.person_country for p in cls.obj.values())
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    @classmethod
    def age_distribution(cls):
        """Distribuição por grupo etário."""
        groups = {'18-25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56-65': 0}
        for p in cls.obj.values():
            age = p.person_age
            if   18 <= age <= 25: groups['18-25'] += 1
            elif 26 <= age <= 35: groups['26-35'] += 1
            elif 36 <= age <= 45: groups['36-45'] += 1
            elif 46 <= age <= 55: groups['46-55'] += 1
            elif 56 <= age <= 65: groups['56-65'] += 1
        return list(groups.items())

    def __str__(self):
        return f'Id:{self._id}, Name:{self._person_name}, Email:{self._person_email}'
