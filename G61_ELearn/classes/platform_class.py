"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Platform
"""
from collections import defaultdict, Counter
from classes.gclass import Gclass

class Platform(Gclass):
    obj     = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_platform_name', '_platform_country']
    header  = 'Platform'
    des     = ['Id', 'Name', 'Country']

    def __init__(self, id, platform_name, platform_country):
        super().__init__()
        id = Platform.get_id(int(float(id)))
        self._id               = id
        self._platform_name    = str(platform_name)
        self._platform_country = str(platform_country)
        Platform.obj[id] = self
        Platform.lst.append(id)

    @property
    def id(self): return self._id

    @property
    def platform_name(self): return self._platform_name
    @platform_name.setter
    def platform_name(self, v): self._platform_name = str(v)

    @property
    def platform_country(self): return self._platform_country
    @platform_country.setter
    def platform_country(self, v): self._platform_country = str(v)


    @classmethod
    def revenue_per_platform(cls, trans_obj, top_n=10):
        """Receita total gerada por cada plataforma (top N)."""
        totals = defaultdict(float)
        for t in trans_obj.values():
            totals[t._platform_id] += t._certificate_fee
        ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:top_n]
        result = []
        for pid, rev in ranked:
            name = cls.obj[pid].platform_name if pid in cls.obj else f'Platform {pid}'
            result.append({'id': pid, 'name': name, 'revenue': round(rev, 2)})
        return result

    @classmethod
    def transactions_per_platform(cls, trans_obj, top_n=10):
        """Número de transações por plataforma (top N)."""
        counts = Counter(t._platform_id for t in trans_obj.values())
        ranked = counts.most_common(top_n)
        result = []
        for pid, count in ranked:
            name = cls.obj[pid].platform_name if pid in cls.obj else f'Platform {pid}'
            result.append({'id': pid, 'name': name, 'count': count})
        return result

    @classmethod
    def platforms_per_country(cls):
        """Número de plataformas por país."""
        counts = Counter(p.platform_country for p in cls.obj.values())
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)

    @classmethod
    def avg_revenue_per_platform(cls, trans_obj):
        """Receita média por plataforma."""
        totals = defaultdict(float)
        for t in trans_obj.values():
            totals[t._platform_id] += t._certificate_fee
        if not totals:
            return 0.0
        return round(sum(totals.values()) / len(totals), 2)

    def __str__(self):
        return f'Id:{self._id}, Name:{self._platform_name}, Country:{self._platform_country}'
