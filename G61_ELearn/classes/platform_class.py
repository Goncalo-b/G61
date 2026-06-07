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
    def id(self): 
        return self._id

    @property
    def platform_name(self): 
        return self._platform_name
    
    @platform_name.setter
    def platform_name(self, v): 
        self._platform_name = str(v)

    @property
    def platform_country(self): 
        return self._platform_country
    
    @platform_country.setter
    def platform_country(self, v): 
        self._platform_country = str(v)

    @classmethod
    def revenue_per_platform(cls, trans_obj, top_n=10):
        totals = {}
        for t in trans_obj.values():
            pid = t._platform_id
            if pid not in totals:
                totals[pid] = 0.0
            totals[pid] += t._certificate_fee

        pairs = []
        for pid, rev in totals.items():
            pairs.append((pid, rev))
        pairs.sort(key=lambda x: x[1], reverse=True)

        result = []
        for pid, rev in pairs[:top_n]:
            if pid in cls.obj:
                name = cls.obj[pid].platform_name
            else:
                name = 'Platform ' + str(pid)
            result.append({'id': pid, 'name': name, 'revenue': round(rev, 2)})
        return result

    @classmethod
    def transactions_per_platform(cls, trans_obj, top_n=10):
        counts = {}
        for t in trans_obj.values():
            pid = t._platform_id
            if pid not in counts:
                counts[pid] = 0
            counts[pid] += 1

        pairs = []
        for pid, count in counts.items():
            pairs.append((pid, count))
        pairs.sort(key=lambda x: x[1], reverse=True)

        result = []
        for pid, count in pairs[:top_n]:
            if pid in cls.obj:
                name = cls.obj[pid].platform_name
            else:
                name = 'Platform ' + str(pid)
            result.append({'id': pid, 'name': name, 'count': count})
        return result

    @classmethod
    def platforms_per_country(cls):
        counts = {}
        for p in cls.obj.values():
            country = p.platform_country
            if country not in counts:
                counts[country] = 0
            counts[country] += 1

        pairs = []
        for country, count in counts.items():
            pairs.append((country, count))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs

    @classmethod
    def avg_revenue_per_platform(cls, trans_obj):
        totals = {}
        for t in trans_obj.values():
            pid = t._platform_id
            if pid not in totals:
                totals[pid] = 0.0
            totals[pid] += t._certificate_fee
        if not totals:
            return 0.0
        return round(sum(totals.values()) / len(totals), 2)

    def __str__(self):
        return 'Id:' + str(self._id) + ', Name:' + self._platform_name + ', Country:' + self._platform_country
