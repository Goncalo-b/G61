"""
@author: Grupo 61 - FEUP PC II 2025/2026
objective: class Person
"""
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

    def __str__(self):
        return f'Id:{self._id}, Name:{self._person_name}, Email:{self._person_email}'
