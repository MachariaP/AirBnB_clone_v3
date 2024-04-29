#!/usr/bin/python3
"""
BaseModel Class of Models Module
"""

import os
import json
import models
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime

storage_type = os.environ.get('HBNB_TYPE_STORAGE')

if storage_type == 'db':
    Base = declarative_base()
else:
    class Base:
        pass


class BaseModel:
    if storage_type == 'db':
        id = Column(String(60), nullable=False, primary_key=True)
        created_at = Column(DateTime, nullable=False,
                            default=datetime.utcnow())
        updated_at = Column(DateTime, nullable=False,
                            default=datetime.utcnow())

    def __init__(self, *args, **kwargs):
        if kwargs:
            self.__set_attributes(kwargs)
        else:
            self.id = str(uuid4())
            self.created_at = datetime.now()

    def __set_attributes(self, attr_dict):
        if 'id' not in attr_dict:
            attr_dict['id'] = str(uuid4())
        if 'created_at' not in attr_dict:
            attr_dict['created_at'] = datetime.now()
        elif not isinstance(attr_dict['created_at'], datetime):
            attr_dict['created_at'] = datetime.strptime(
                attr_dict['created_at'], '%Y-%m-%d %H:%M:%S.%f')
        if 'updated_at' in attr_dict:
            if not isinstance(attr_dict['updated_at'], datetime):
                attr_dict['updated_at'] = datetime.strptime(
                    attr_dict['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
        if storage_type != 'db':
            if attr_dict['__class__']:
                attr_dict.pop('__class__')
        for attr, val in attr_dict.items():
            setattr(self, attr, val)

    def __is_serializable(self, obj_v):
        try:
            obj_to_str = json.dumps(obj_v)
            return obj_to_str is not None and isinstance(obj_to_str, str)
        except:
            return False

    def bm_update(self, name, value):
        setattr(self, name, value)
        if storage_type != 'db':
            self.save()

    def save(self):
        if storage_type != 'db':
            self.updated_at = datetime.now()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self, save_to_disk=False):
        new_dict = self.__dict__.copy()
        new_dict['__class__'] = self.__class__.__name__

        if 'password' in new_dict and not save_to_disk:
            del new_dict['password']

        if '_sa_instance_state' in new_dict:
            del new_dict['_sa_instance_state']

        return new_dict

    def __str__(self):
        class_name = type(self).__name__
        return '[{}] ({}) {}'.format(class_name, self.id, self.__dict__)

    def delete(self):
        models.storage.delete(self)
