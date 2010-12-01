#!/usr/bin/env python
# encoding: utf-8
"""Python client for OrientDB REST serivce"""

import base64
import datetime
import re
import collections
import httplib
import time
from urlparse import urlsplit
import urllib
import decimal
import string

from request import Request

try:
    import json
except ImportError:
    import simplejson as json

RECORD_ID = '@rid'

ADMIN = ('admin', 'admin')
READER = ('reader', 'reader')
WRITER = ('writer', 'writer')
    
class CompassException(Exception):
    pass

class BaseObject(object):
    data = {}
    id = None
    
    def save(self):
        pass
    
    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        if key.startswith('_'):
            raise KeyError('')
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]


class Server(BaseObject):
    action = {
        'info': '%s/server'
    }
    
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.request = Request(self.username, self.password)
        
    def info(self):
        url = self.action['info'] % (self.url)
        response, content = self.request.get(url=url) 
        
        if response.status == 200:
            self.data = json.loads(content)
            return
        else:
            raise CompassException(content)
            
        return self
            
    def database(self, name, credentials=ADMIN, create=False):
        if create:
            url =  Database.action['get'] % (self.url, name)
            response, content = self.request.post(url=url, data=None)

            if response.status == 204:
                return self.database(name=name, credentials=ADMIN)
            else:
                raise CompassException(content)
        elif len(credentials) == 2:
            url = Database.action['post'] % (self.url, name)
            user, password = credentials
            request = Request(user, password)
            response, content = request.get(url=url)
        
            if response.status == 200:
                data = json.loads(content)
                return Database(self.url, name=name, credentials=credentials, data=data).connect()
            else:
                raise CompassException(content)
        

class Database(BaseObject):
    action = {
        'connect': '%s/connect/%s',
        'get': '%s/database/%s',
        'post': '%s/database/%s',
        'query': '%s/command/%s/%s/%s',
        'cluster': '%s/cluster/%s/%s'
    }
    
    def __init__(self, url, name, credentials, data=None):
        self.url = url
        self.name = name
        self.credentials = credentials
        self.request = Request(username=credentials[0], password=credentials[1])

        if data is None:
            self.connect()
        else: 
            self.data = data
        
    def connect(self):
        url = self.action['connect'] % (self.url, self.name)        
        response, content = self.request.get(url)

        if response.status == 200:
            self.data = json.loads(content)
        else:
            raise CompassException(content)
            
        return self
        
    def cluster(self, class_name):
        url = Cluster.action['get'] % (self.url, self.name, class_name)
        response, content = self.request.get(url)
        
        if response.status == 200:
            return Cluster(database=self, data=json.loads(content))
        else:
            raise CompassException(content)
            
        
    def klass(self, name, limit=20, create=False):
        if create:
            url = Klass.action['post'] % (self.url, self.name, name)
            response, content = self.request.post(url, data={})

            if response.status == 201:
                return self.klass(name=name)
            else: 
                raise CompassException(content)
        else:
            url = Klass.action['get'] % (self.url, self.name, name, limit)
            response, content = self.request.get(url)

            if response.status == 200:
                data = json.loads(content)

                return Klass(database=self, documents=data['result'])
            else: 
                raise CompassException(content)
            
        
    def query(self, query):
        query = urllib.quote(query)
        url = self.action['query'] % (self.url, self.name, self.name, query)
        response, content = self.request.post(url, data={})

        if response.status == 200:
            result = json.loads(content)
                
            return Klass(database=self, documents=result['result'])
        else:
            raise CompassException(content)
            
        
    def document(self, id=None, **data):
        if id:
            url = Document.action['get'] % (self.url, self.name, id)
            response, content = self.request.get(url)
            
            if response.status == 200:
                return Document(id, json.loads(content), database=self)
            else:
                raise CompassException(content)            
        else:
            url = Document.action['post'] % (self.url, self.name)
            response, content = self.request.post(url, data=data)

            if response.status == 201:
                return self.document(id=content, database=self)
            else:
                raise CompassException(content)
                
        

class Cluster(BaseObject):
    action = {
        'get': '%s/cluster/%s/%s'
    }
    
    def __init__(self, database, data):
        self.database = database
        self.data = data
                

class Klass(BaseObject):
    action = {
        'get': '%s/class/%s/%s/%s',
        'post': '%s/class/%s/%s'
    }
    
    def __init__(self, database, schema={}, documents={}):
        self.database = database
        self.schema = schema
        
        for data in documents:
            self.data[data[RECORD_ID]] = Document(data['@rid'], data, klass=self)
            
    def document(self, id=None, **data):
        if id:
            url = Document.action['get'] % (self.database.url, self.database.name, id)
            response, content = self.request.get(url)
            
            if response.status == 200:
                return Document(id, json.loads(content), database=self)
            else:
                raise CompassException(content)            
        else:
            url = Document.action['post'] % (self.database.url, self.database.name)
            response, content = self.request.post(url, data=data)

            if response.status == 201:
                return self.document(id=content, database=self)
            else:
                raise CompassException(content)
            
    @property
    def id(self):
        return self.schema['id']
        
    @property
    def name(self):
        return self.schema['name']


class Document(BaseObject):
    action = {
        'get': '%s/document/%s/%s',
        'post': '%s/document/%s',
        'put': '%s/document/%s',
        'delete': '%s/document/%s/%s'
    }
    
    def __init__(self, id, data, database=None, klass=None):
        self.id = id
        self.data = data
        self.database = database
        self.klass = klass
        
        if self.database is not None:
            self.db_url = self.database.url
            self.db_name = self.database.name
            self.db_request = self.database.request
        else:
            self.db_url = self.klass.database.url
            self.db_name = self.klass.database.name
            self.db_request = self.klass.database.request
        
    def save(self):
        url = self.action['put'] % (self.db_url, self.db_name)
        response, content = self.db_request.put(url=url, data= self.data)

        if response.status == 200:
            return self
        else:
            raise CompassException(content)
            
    def relate(self, field, document=None, id=None, multiple=False):
        if document is not None:
            id = document[RECORD_ID]
        
        if multiple:
            if isinstance(self[field], list):
                ids = self[field]
                
                if id not in ids:
                    ids.append(id)
                
                self[field] = ids
        else:
            self[field] = id
            
        return self
        
    def delete(self):
        url = self.action['delete'] % (self.db_url, self.db_name, self.id)
        response, content = self.db_request.delete(url=url)
        
        if response.status != 204:
            raise CompassException(content)
        
        