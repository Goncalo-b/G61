from classes.gclass import Gclass

class Student(Gclass):
    obj     = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_student_name', '_student_email', '_student_country', '_student_age']
    header  = 'Student'
    des     = ['Id', 'Name', 'Email', 'Country', 'Age']

    def __init__(self, id, student_name, student_email, student_country='', student_age=0):
        super().__init__()
        id = Student.get_id(int(float(id)))
        self._id              = id
        self._student_name    = str(student_name)
        self._student_email   = str(student_email)
        self._student_country = str(student_country)
        if str(student_age) != '':
            self._student_age = int(float(student_age))
        else:
            self._student_age = 0
        Student.obj[id] = self
        Student.lst.append(id)

    @property
    def id(self): return self._id

    @property
    def student_name(self): return self._student_name
    @student_name.setter
    def student_name(self, v): self._student_name = str(v)

    @property
    def student_email(self): return self._student_email
    @student_email.setter
    def student_email(self, v): self._student_email = str(v)

    @property
    def student_country(self): return self._student_country
    @student_country.setter
    def student_country(self, v): self._student_country = str(v)

    @property
    def student_age(self): return self._student_age
    @student_age.setter
    def student_age(self, v):
        if str(v) != '':
            self._student_age = int(float(v))
        else:
            self._student_age = 0

    @classmethod
    def top_spenders(cls, trans_obj, top_n=10):
        totals = {}
        for t in trans_obj.values():
            pid = t._student_id
            if pid not in totals:
                totals[pid] = 0.0
            totals[pid] += t._certificate_fee

        pairs = []
        for pid, total in totals.items():
            pairs.append((pid, total))
        pairs.sort(key=lambda x: x[1], reverse=True)

        result = []
        for pid, total in pairs[:top_n]:
            if pid in cls.obj:
                name    = cls.obj[pid].student_name
                country = cls.obj[pid].student_country
            else:
                name    = 'Student ' + str(pid)
                country = ''
            result.append({'id': pid, 'name': name, 'country': country,
                           'total': round(total, 2)})
        return result

    @classmethod
    def most_active(cls, trans_obj, top_n=10):
        counts = {}
        for t in trans_obj.values():
            pid = t._student_id
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
                name = cls.obj[pid].student_name
            else:
                name = 'Student ' + str(pid)
            result.append({'id': pid, 'name': name, 'count': count})
        return result

    @classmethod
    def distribution_by_country(cls):
        counts = {}
        for p in cls.obj.values():
            country = p.student_country
            if country not in counts:
                counts[country] = 0
            counts[country] += 1

        pairs = []
        for country, count in counts.items():
            pairs.append((country, count))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs

    @classmethod
    def age_distribution(cls):
        groups = {'18-25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56-65': 0}
        for p in cls.obj.values():
            age = p.student_age
            if 18 <= age <= 25:
                groups['18-25'] += 1
            elif 26 <= age <= 35:
                groups['26-35'] += 1
            elif 36 <= age <= 45:
                groups['36-45'] += 1
            elif 46 <= age <= 55:
                groups['46-55'] += 1
            elif 56 <= age <= 65:
                groups['56-65'] += 1

        result = []
        for key, count in groups.items():
            result.append((key, count))
        return result

    def __str__(self):
        return 'Id:' + str(self._id) + ', Name:' + self._student_name + ', Email:' + self._student_email
