#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import unittest
from client import *
import random

username = 'root'
password = 'AFE1D46E7A5FC722CBD5821644B03BD57CC782B7A1585D438A0414CE0B8DE73D'
url = 'http://localhost:2480'
server = Server(url=url, username=username, password=password)

#dont fail me!
def randomName(prefix, loop=2):
    def randomNumber():
        return random.randrange(random.randint(1, 10000), random.randint(10001, 99999), 4)
        
    name = [prefix]
    
    while loop > -1:
        name.append(str(randomNumber()))
        loop -= 1
        
    return '_'.join(name)
    
    
db_name = randomName('test_DB_', 4)
class_db_name = randomName('database_', 2)
doc_db_name = randomName('doc_db', 1)
doc_name = randomName('document_', 3)
doc_class_name = randomName('doc_class', 2)
class_name = randomName('class_name_', 1)
document_id = ''

class ServerTests(unittest.TestCase):
    def test_can_retrieve_server_info(self):
        try:
            info = server.info()
            result = True
            
            if 'storages' not in server:
                result = False
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        

class CreationTests(unittest.TestCase):
    def setUp(self):
        self.db_name = db_name
        
    def test_can_create_database(self):
        try:
            server.database(name=self.db_name, create=True)
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_create_class(self):
        try:
            database = server.database(name=class_db_name, create=True)
            database.klass(name=class_name, create=True)
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_create_document_on_database(self):
        try:
            global document_id 
            
            database = server.database(name=doc_db_name, create=True)
            document = database.document(name=doc_name, data={}, create=True)
            document_id= document.id
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
        
class RetrievalTests(unittest.TestCase):
    def test_can_retrieve_database(self):
        try:
            server.database(name=db_name)
            result = True
        except CompassException, e:
            result = False
        
        self.assertTrue(result)
        
        
    def test_can_retrieve_class(self):
        try:
            database = server.database(name=class_db_name)
            database.klass(name=class_name)
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)


class DatabaseTests(unittest.TestCase):        
    def test_can_connect_to_database(self):
        try:
            database = server.database(name=db_name)
            
            database.connect()
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_query_database(self):
        try:
            query = 'select * from %s' % (class_name)
            database = server.database(name=class_db_name)
            
            database.query(query=query)
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        

class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.database = server.database(name=doc_db_name)
        
    def test_can_retrieve_document_property(self):
        try:
            global document_id
            document = self.database.document(id=document_id)
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_retrieve_document_value(self):
        try:
            global document_id
            
            document = self.database.document(id=document_id)
            result = True

            document['name']
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_set_document_value(self):
        try:
            global document_id
            
            document = self.database.document(id=document_id)
            result = True
            
            document[u'last name'] = 'ahhhhh'
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_connect_document_by_id(self):
        try:
            global document_id
            
            document = self.database.document(id=document_id)
            document2 = self.database.document(create=True, data={})
            id2 = document2.id
            
            document.relate(field='knows', id=id2)
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_connect_document_by_document(self):
        try:
            global document_id
            
            document = self.database.document(id=document_id)
            document2 = self.database.document(create=True, data={})
            
            document.relate(field='knows', document=document2)
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_save_docuemnt(self):
        try:
            global document_id
            
            document = self.database.document(id=document_id)
            
            document['who'] = 'me'
            
            document.save()
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_delete_document(self):
        try:
            global document_id
            
            document = self.database.document(name='test to be deleted', create=True)
            
            document.delete()
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
    
    

if __name__ == '__main__':
    server_suite = unittest.TestLoader().loadTestsFromTestCase(ServerTests)
    unittest.TextTestRunner(verbosity=3).run(server_suite)
    
    creation_suite = unittest.TestLoader().loadTestsFromTestCase(CreationTests)
    unittest.TextTestRunner(verbosity=3).run(creation_suite)
    
    retrieval_suite = unittest.TestLoader().loadTestsFromTestCase(RetrievalTests)
    unittest.TextTestRunner(verbosity=3).run(retrieval_suite)
    
    database_suite = unittest.TestLoader().loadTestsFromTestCase(DatabaseTests)
    unittest.TextTestRunner(verbosity=3).run(database_suite)
    
    document_suite = unittest.TestLoader().loadTestsFromTestCase(DocumentTests)
    unittest.TextTestRunner(verbosity=3).run(document_suite)