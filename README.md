Compass
=============
Compass is a simple Python REST interface for the OrientDB graph document store. Later iterations of compass will allow you to choose between the REST or BINARY protocols while using the same compass interface.

Requirements
-------------
* Python 2.6 
* OrientDB Rest Server

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
    
    import compass
	import json
    