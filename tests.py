#!/usr/bin/env python
# encoding: utf-8

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
document_rid = ''

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
            global document_rid 
            
            database = server.database(name=doc_db_name, create=True)
            document = database.document(name=doc_name, create=True, first_name='mark')
            document_rid= document.rid
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_create_document_on_class(self):
        try:            
            database = server.database(name=randomName('doc_class_db', 3), create=True)
            klass = database.klass(name=class_name, create=True)
            document = klass.document(name=doc_name, create=True, first_name='MARK')
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_create_property_on_class(self):
        try:
            database = server.database(name=randomName('doc_class_db', 3), create=True)
            klass = database.klass(name=randomName('random_class', 2), create=True)
            klass.property(name=randomName('property', 1))
            
            if len(klass.schema) > 0:
                result = True
            else:
                reslut = False
        except CompassException, e:
            result = False;
            
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
            klass = database.query(query=query)
            
            if isinstance(klass, Klass):
                result = True
            else:
                reslut = False
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        

class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.database = server.database(name=doc_db_name)
        
    def test_can_retrieve_document_value(self):
        try:
            global document_rid
            
            document = self.database.document(rid=document_rid)
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_set_document_value(self):
        try:
            global document_rid
            
            document = self.database.document(rid=document_rid)
            result = True
            
            document[u'last name'] = 'ahhhhh'
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_connect_document_by_rid(self):
        try:
            global document_rid
            
            document = self.database.document(rid=document_rid)
            document2 = self.database.document(create=True, data={})
            id2 = document2.rid
            
            document.relate(field='knows', rid=id2)
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_connect_document_by_document(self):
        try:
            global document_rid
            
            document = self.database.document(rid=document_rid)
            document2 = self.database.document(create=True, data={})
            
            document.relate(field='knows', document=document2)
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_save_docuemnt(self):
        try:
            global document_rid
            
            document = self.database.document(rid=document_rid)
            
            document['who'] = 'me'
            
            document.save()
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
        
    def test_can_delete_document(self):
        try:
            global document_rid
            
            document = self.database.document(name='test to be deleted', create=True)
            
            document.delete()
            
            result = True
        except CompassException, e:
            result = False
            
        self.assertTrue(result)
    

class KlassTests(unittest.TestCase):
    def setUp(self):
        self.database = server.database(name=randomName('class_test_db', 3), create=True)
        self.klass = self.database.klass(name=randomName('random_class', 2), create=True)
    
    def test_can_create_property(self):
        try:
            original_len = len(self.klass.schema)
            
            self.klass.property(name=randomName('prop_', 3))
            
            if len(self.klass.schema) > original_len:
                result = True
            else:
                result = False
        except CompassException, e:
            result = False;
            
        self.assertTrue(result)
        
    def test_can_delete_property(self):
        try:
            self.klass.property(name=randomName('prop1_', 3))
            self.klass.property(name=randomName('prop2_', 3))
            
            original_len = len(self.klass.schema)
            keys = self.klass.schema.keys()
            
            del self.klass.schema[keys[0]]
            
            if len(self.klass.schema) < original_len:
                result = True
            else:
                result = False
        except CompassException, e:
            result = False;
            
        self.assertTrue(result)
        
    def test_can_run_query_and_get_results(self):
        try:
            class_name = randomName('new_class', 2)
            new_class = self.database.klass(name=class_name, create=True)
            doc1 = new_class.document(name=randomName('random_doc', 3))
            doc2 = new_class.document(name=randomName('random_doc', 3))
            query = 'select * from %s' % (class_name)
            new_class.query(query=query)

            if len(new_class) == 2:
                result = True
            else:
                result = False
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
    
    klass_suite = unittest.TestLoader().loadTestsFromTestCase(KlassTests)
    unittest.TextTestRunner(verbosity=3).run(klass_suite)