"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Platform
"""
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

    def __str__(self):
        return f'Id:{self._id}, Name:{self._platform_name}, Country:{self._platform_country}'
