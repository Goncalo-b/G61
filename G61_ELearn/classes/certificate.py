from classes.gclass import Gclass

class Certificate(Gclass):
    obj     = dict()
    _by_id  = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_certificate_name', '_certificate_type', '_certificate_language', '_issue_date']
    header  = 'Certificate'
    des     = ['Id', 'Name', 'Type', 'Language', 'Issue Date']
    _seq    = 0

    def __init__(self, id, certificate_name, certificate_type,
                 certificate_language='', issue_date=''):
        super().__init__()
        Certificate._seq += 1
        self._rowkey               = Certificate._seq
        self._id                   = Certificate.get_id(int(float(id)))
        self._certificate_name     = str(certificate_name)
        self._certificate_type     = str(certificate_type)
        self._certificate_language = str(certificate_language)
        if str(issue_date) not in ('', 'None'):
            self._issue_date = str(issue_date)[:10]
        else:
            self._issue_date = ''
        Certificate.obj[self._rowkey] = self
        Certificate.lst.append(self._rowkey)
        if self._id not in Certificate._by_id:
            Certificate._by_id[self._id] = self

    @classmethod
    def get_by_id(cls, db_id):
        return cls._by_id.get(int(db_id))

    @property
    def id(self): return self._id

    def get_key(self): return self._rowkey

    @classmethod
    def get_id(cls, id):
        id = int(id)
        if id == 0:
            existing = list(cls._by_id.keys())
            if existing:
                return max(existing) + 1
            return 1
        return id

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

    @property
    def issue_date(self): return self._issue_date
    @issue_date.setter
    def issue_date(self, v):
        if str(v) not in ('', 'None'):
            self._issue_date = str(v)[:10]
        else:
            self._issue_date = ''

    @classmethod
    def read(cls, path=''):
        cls.obj    = dict()
        cls._by_id = dict()
        cls.lst    = list()
        cls._seq   = 0
        cls.pos    = 0
        cls.path   = path
        try:
            rows = cls.sqlexe("SELECT * FROM Certificate ORDER BY id")
            if rows:
                for r in rows:
                    cls(*r)
        except Exception as err:
            print('Certificate.read error: ' + str(err))

    @classmethod
    def remove(cls, p):
        obj = cls.obj[p]
        cls.sqlexe(
            "DELETE FROM Certificate WHERE rowid = "
            "(SELECT rowid FROM Certificate WHERE id=" + str(obj._id) + " LIMIT 1)"
        )
        cls.lst.remove(p)
        del cls.obj[p]
        cls._by_id.pop(obj._id, None)
        for o in cls.obj.values():
            if o._id == obj._id:
                cls._by_id[obj._id] = o
                break

    @classmethod
    def insert(cls, p):
        obj = cls.obj[p]
        cls.sqlexe(
            'INSERT INTO Certificate VALUES(' +
            str(obj._id) + ',"' + obj._certificate_name + '","' +
            obj._certificate_type + '","' + obj._certificate_language +
            '","' + obj._issue_date + '")'
        )

    @classmethod
    def update(cls, p):
        obj = cls.obj[p]
        cls.sqlexe(
            'UPDATE Certificate SET '
            'certificate_name="' + obj._certificate_name + '", '
            'certificate_type="' + obj._certificate_type + '", '
            'certificate_language="' + obj._certificate_language + '", '
            'issue_date="' + obj._issue_date + '" '
            'WHERE rowid=(SELECT rowid FROM Certificate WHERE id=' + str(obj._id) + ' LIMIT 1)'
        )

    @classmethod
    def issued_by_year(cls):
        counts = {}
        for c in cls.obj.values():
            if c._issue_date:
                year = c._issue_date[:4]
                if year not in counts:
                    counts[year] = 0
                counts[year] += 1

        result = []
        for year in sorted(counts.keys()):
            result.append((year, counts[year]))
        return result

    @classmethod
    def most_issued(cls, trans_obj, top_n=10):
        counts = {}
        for t in trans_obj.values():
            cid = t._certificate_id
            if cid not in counts:
                counts[cid] = 0
            counts[cid] += 1

        pairs = []
        for cid, count in counts.items():
            pairs.append((cid, count))
        pairs.sort(key=lambda x: x[1], reverse=True)

        result = []
        for cid, count in pairs[:top_n]:
            obj = cls.get_by_id(cid)
            if obj:
                name  = obj._certificate_name
                ctype = obj._certificate_type
            else:
                name  = 'Cert ' + str(cid)
                ctype = ''
            result.append({'id': cid, 'name': name, 'type': ctype, 'count': count})
        return result

    @classmethod
    def distribution_by_type(cls):
        counts = {}
        for c in cls.obj.values():
            ctype = c._certificate_type
            if ctype not in counts:
                counts[ctype] = 0
            counts[ctype] += 1

        pairs = []
        for ctype, count in counts.items():
            pairs.append((ctype, count))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs

    @classmethod
    def distribution_by_language(cls):
        counts = {}
        for c in cls.obj.values():
            lang = c._certificate_language
            if lang not in counts:
                counts[lang] = 0
            counts[lang] += 1

        pairs = []
        for lang, count in counts.items():
            pairs.append((lang, count))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs

    @classmethod
    def avg_fee_by_type(cls, trans_obj):
        totals = {}
        counts = {}
        for t in trans_obj.values():
            obj = cls.get_by_id(t._certificate_id)
            if obj:
                ctype = obj._certificate_type
                if ctype not in totals:
                    totals[ctype] = 0.0
                    counts[ctype] = 0
                totals[ctype] += t._certificate_fee
                counts[ctype] += 1

        result = []
        for ctype in totals:
            avg = round(totals[ctype] / counts[ctype], 2)
            result.append({'type': ctype, 'avg_fee': avg, 'count': counts[ctype]})
        result.sort(key=lambda x: x['avg_fee'], reverse=True)
        return result

    def __str__(self):
        return 'Id:' + str(self._id) + ', Name:' + self._certificate_name + ', Type:' + self._certificate_type
