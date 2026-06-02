"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Course
"""
from classes.gclass import Gclass

class Course(Gclass):
    obj     = dict()
    lst     = list()
    pos     = 0
    sortkey = ''
    att     = ['_id', '_course_name', '_course_category', '_course_info', '_online_date', '_platform_id']
    header  = 'Course'
    des     = ['Id', 'Name', 'Category', 'Info', 'Online Date', 'Platform Id']

    def __init__(self, id, course_name, course_category, course_info, online_date, platform_id):
        super().__init__()
        id = Course.get_id(int(float(id)))
        self._id              = id
        self._course_name     = str(course_name)
        self._course_category = str(course_category)
        self._course_info     = str(course_info)
        self._online_date     = str(online_date)
        self._platform_id     = int(float(platform_id))
        Course.obj[id] = self
        Course.lst.append(id)

    @property
    def id(self): return self._id

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

    def __str__(self):
        return f'Id:{self._id}, Name:{self._course_name}, Category:{self._course_category}'
