Server Objects and Object Generators
====================================
In Ockle, a server holds a collection of *Server Objects* which the Ockle's :doc:`plugins` interact with.
A server object instance is created from an *Object Generator* class. Currently there are three Object Generator are: PDUs, Controllers and Testers. Those generate the Outlet, control and test objects respectively.

.. toctree::   
   PDUs
   Controllers
   Testers


Object Generators common tools 
--------------------------------------------

INI Template files
~~~~~~~~~~~~~~~~~~

You can specify global parameters for the PDU, controllers and testers and specific parameters for each server outlet, control and test.

*Object Generator* parameters go in a section named after that object generator.
For example, PDUs have a ``[pdu]`` section.

*Server Object* parameters on in a section named after the Server Object, followed by the word Params.
For example an outlet will will have an ``[outletParams]`` section.

These template files follow Ockle's :doc:`INITemplates` .


