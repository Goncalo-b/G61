"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Certificate
"""
from collections import defaultdict, Counter
from classes.gclass import Gclass

class Certificate(Gclass):
    obj     = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_certificate_name', '_certificate_type', '_certificate_language']
    header  = 'Certificate'
    des     = ['Id', 'Name', 'Type', 'Language']

    def __init__(self, id, certificate_name, certificate_type, certificate_language=''):
        super().__init__()
        id = Certificate.get_id(int(float(id)))
        self._id                   = id
        self._certificate_name     = str(certificate_name)
        self._certificate_type     = str(certificate_type)
        self._certificate_language = str(certificate_language)
        Certificate.obj[id] = self
        Certificate.lst.append(id)

    @property
    def id(self): return self._id

    @property
    def certificate_name(self): return self._certificate_name
    @certificate_name.setter
    def certificate_name(self, v): self._certificate_name = str(v)

    @property
    def certificate_type(self): return self._certificate_type
    @certificate_type.setter
    def certificate_type(self, v): self._certificate_type = str(v)

    @property
    def certificate_language(self): return self._certificate_language
    @certificate_language.setter
    def certificate_language(self, v): self._certificate_language = str(v)


    @classmethod
    def most_issued(cls, trans_obj, top_n=10):
        counts = Counter(t._certificate_id for t in trans_obj.values())
        result = []
        for cid, count in counts.most_common(top_n):
            name = cls.obj[cid].certificate_name if cid in cls.obj else f'Cert {cid}'
            ctype = cls.obj[cid].certificate_type if cid in cls.obj else ''
            result.append({'id': cid, 'name': name, 'type': ctype, 'count': count})
        return result

    @classmethod
    def distribution_by_type(cls):
        counts = Counter(c.certificate_type for c in cls.obj.values())
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    @classmethod
    def distribution_by_language(cls):
        counts = Counter(c.certificate_language for c in cls.obj.values())
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    @classmethod
    def avg_fee_by_type(cls, trans_obj):
        totals = defaultdict(float)
        counts = defaultdict(int)
        for t in trans_obj.values():
            if t._certificate_id in cls.obj:
                ctype = cls.obj[t._certificate_id].certificate_type
                totals[ctype] += t._certificate_fee
                counts[ctype] += 1
        result = []
        for ctype in totals:
            result.append({
                'type': ctype,
                'avg_fee': round(totals[ctype] / counts[ctype], 2),
                'count': counts[ctype]
            })
        return sorted(result, key=lambda x: x['avg_fee'], reverse=True)

    def __str__(self):
        return f'Id:{self._id}, Name:{self._certificate_name}, Type:{self._certificate_type}'
