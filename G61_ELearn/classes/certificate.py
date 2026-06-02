"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Certificate
"""
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

    def __str__(self):
        return f'Id:{self._id}, Name:{self._certificate_name}, Type:{self._certificate_type}'
