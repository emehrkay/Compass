Compass
=============
Compass is a simple Python REST interface for the OrientDB graph document store. Later iterations of compass will allow you to choose between the REST or BINARY protocols while using the same compass interface.

Requirements
-------------
* Python 2.6 
* [OrientDB Rest Server](http://www.orientechnologies.com/)

Classes
-------------
Compass provides seven classes that represent OrientDB objects. 

* **CompassException** -- the exception object that is returned when things go wrong.
* **BaseObject** -- all other objects extend this one. It provides a simple interface for save and delete and adds some dict-like interactions via member getters, setters, and iterations
* **Server** -- the root object for all Compass interactions. Allows creation and retrieval of databases (Database).
* **Database** -- most actions are taken directly against the Database object. Allows creation and retrieval of classes (Klass) and documents (Document).
* **Klass** -- this object is though of as a table, like documents (Document) can be easily grouped by class. A class has a schema and Klass allows for creation and removal of properties in that schema (KlassProperty) and documents (Document) for that class.
* **Cluster** -- all of the physical or logical cluster information
* **KlassProperty** -- holds all of the information about a class (Klass) property.
* **Document** -- this object represents a single record in the database (Database) or class (Klass)

Usage
-------------
Using compass is simple, all failures will raise a CompassException.
    
**Imports**
    
    import compass
	import json
	
**Exceptions**
All actions throw a CompassException if it happens to fail. Good practice would be to wrap all code in a try except construct to capture any errors.

    try:
        server = client.server(url='http://localhost:2480')
    except CompassException, e:
        print e #should return a 401 with an error message
    
	
**Server Connection**
To connect to the server you need to locate the user defined in the orientdb-server-config.xml file. Once you start the server for the first time, the user is root and the password is automatically generated.
    
    user = 'root'
    password = 'EDEBF121682BF71D0DEDB82459E6B772CDD291F3C0765D7C6B104420604F269C'
    url = 'http://localhost:2480'
    server = client.Server(url=url, username=username, password=password)
    
**Database Interactions**
Connect to or retrieve an existing database. Upon database creation, three users are created; admin, writer, and reader. Those are defined as a simple tuple so if you create a custom user, store the credentials as such.
    
    #create a demo database
    demo_db = server.database(name='client_demo', create=True, 
                              credentials=client.ADMIN)
                              
    #add a new class to the database
    address_class = demo_db.klass(name='Address', create=True)
    
    #add a document directly to that class
    apple_doc = address_class.document(address1='1 Infinite Loop', 
                                       city='Cupertino', state='CA', zip='95014')
                                       
    #add another document to the database object, but give it the class 'Address'
    microsoft_doc = demo_db.document(class_name='Address', address1='One Microsoft Way'...)
    
    #query documents this returns a Klass object with its data member made up of Document objects. 
    #The key is the record_id (@rid) and value is the Document object
    result_klass = demo_db.query('SELECT * FROM Address WHERE city = "Cupertino"')
    
**Klass Object**
The class object will eventually allow you to define a schema for all documents that belong to it. The latest build of OrientDB's rest server does not allow for creation of properties that define certain attributes (required, max, min length, etc), it will in a later release

    #retrieve a class
    addresses = demo_db.klass(name='Address')
    
    #add a property to the schema
    addresses.property(name='country')
    
    #display the schema 
    print addresses.schema # [dict] key is the property name, value is a KlassProperty object
    
    #modify a property -- this will matter in a future release, the save interface is not defined yet
    country_prop = addresses.schema['country']
    country_prop['required'] = True
    
    #remove a property
    addresses.schema['country'].delete()
    
**Document**
Documents should be created from a Database or Klass object, it is possible to create a document using the Document constructor, but a Database or Klass needs to be passed in as an argument.

    #update a document
    apple_doc['country'] = 'USA'
    
    #save
    apple_doc.save()
    
    #delete
    apple_doc.delete()
    
    #connect a document to another one
    #multiple will store the connections as a list
    other_document = demo_db.document(field='Value')
    apple_doc.relate(field='connections', document=other_document, multiple=True)