from classes.gclass import Gclass

class Course(Gclass):
    obj     = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_course_name', '_course_category', '_course_info', '_online_date', '_platform_id']
    header  = 'Course'
    des     = ['Id', 'Name', 'Category', 'Info', 'Online Date', 'Platform Id']
    _seq    = 0

    def __init__(self, id, course_name, course_category, course_info, online_date, platform_id):
        super().__init__()
        Course._seq += 1
        self._rowkey          = Course._seq
        self._id              = Course.get_id(int(float(id)))
        self._course_name     = str(course_name)
        self._course_category = str(course_category)
        self._course_info     = str(course_info)
        self._online_date     = str(online_date)
        if str(platform_id).strip() not in ('', 'None'):
            self._platform_id = int(float(platform_id))
        else:
            self._platform_id = 0
        Course.obj[self._rowkey] = self
        Course.lst.append(self._rowkey)

    @property
    def id(self): return self._id

    def get_key(self): return self._rowkey

    @classmethod
    def get_id(cls, id):
        id = int(id)
        if id == 0:
            existing = []
            for o in cls.obj.values():
                existing.append(o._id)
            if existing:
                return max(existing) + 1
            return 1
        return id

    @property
    def course_name(self): return self._course_name
    @course_name.setter
    def course_name(self, v): self._course_name = str(v)

    @property
    def course_category(self): return self._course_category
    @course_category.setter
    def course_category(self, v): self._course_category = str(v)

    @property
    def course_info(self): return self._course_info
    @course_info.setter
    def course_info(self, v): self._course_info = str(v)

    @property
    def online_date(self): return self._online_date
    @online_date.setter
    def online_date(self, v): self._online_date = str(v)

    @property
    def platform_id(self): return self._platform_id
    @platform_id.setter
    def platform_id(self, v): self._platform_id = int(float(v))

    @classmethod
    def read(cls, path=''):
        cls.obj  = dict()
        cls.lst  = list()
        cls._seq = 0
        cls.pos  = 0
        cls.path = path
        try:
            rows = cls.sqlexe("SELECT * FROM Course ORDER BY id")
            if rows:
                for r in rows:
                    cls(*r)
        except Exception as err:
            print('Course.read error: ' + str(err))

    @classmethod
    def remove(cls, p):
        obj = cls.obj[p]
        cls.sqlexe(
            "DELETE FROM Course WHERE rowid = "
            "(SELECT rowid FROM Course WHERE id=" + str(obj._id) + " LIMIT 1)"
        )
        cls.lst.remove(p)
        del cls.obj[p]

    @classmethod
    def insert(cls, p):
        obj = cls.obj[p]
        cls.sqlexe(
            'INSERT INTO Course VALUES(' +
            str(obj._id) + ',"' + obj._course_name + '","' +
            obj._course_category + '","' + obj._course_info +
            '","' + obj._online_date + '",' + str(obj._platform_id) + ')'
        )

    @classmethod
    def update(cls, p):
        obj = cls.obj[p]
        cls.sqlexe(
            'UPDATE Course SET '
            'course_name="' + obj._course_name + '", '
            'course_category="' + obj._course_category + '", '
            'course_info="' + obj._course_info + '", '
            'online_date="' + obj._online_date + '", '
            'platform_id=' + str(obj._platform_id) + ' '
            'WHERE rowid=(SELECT rowid FROM Course WHERE id=' + str(obj._id) + ' LIMIT 1)'
        )

    @classmethod
    def distribution_by_category(cls):
        counts = {}
        for c in cls.obj.values():
            cat = c._course_category
            if cat not in counts:
                counts[cat] = 0
            counts[cat] += 1

        pairs = []
        for cat, count in counts.items():
            pairs.append((cat, count))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs

    @classmethod
    def courses_per_platform(cls, top_n=10):
        counts = {}
        for c in cls.obj.values():
            pid = c._platform_id
            if pid not in counts:
                counts[pid] = 0
            counts[pid] += 1

        pairs = []
        for pid, count in counts.items():
            pairs.append((pid, count))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs[:top_n]

    @classmethod
    def courses_added_by_year(cls):
        counts = {}
        for c in cls.obj.values():
            if c._online_date and c._online_date != 'None':
                year = str(c._online_date)[:4]
                if year.isdigit():
                    if year not in counts:
                        counts[year] = 0
                    counts[year] += 1

        result = []
        for year in sorted(counts.keys()):
            result.append((year, counts[year]))
        return result

    def __str__(self):
        return 'Id:' + str(self._id) + ', Name:' + self._course_name + ', Category:' + self._course_category
