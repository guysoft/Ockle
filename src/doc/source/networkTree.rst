Ockle's Network Tree Data Structure
===================================

The Whole Network Tree
----------------------
Ockle's main data structure is a acyclic graph implemented by pygraph_, that lives in an instance of networkTree/ServerNetwork.py . This graph holds ServerNodes instances, each one represents a server.

You can build a server network from Ockle's ini files using the :doc:`ServerNetworkFactory`

.. autoclass:: networkTree.ServerNetwork.ServerNetwork
   :members:
   
A Server Node Within the Network
---------------------------------
The Server Node object holds the global operation state of the server, and methods to control the server as a whole. Server objects are also stored in this instance.
Currently server objects are: Outlets, Controls and Tests.

.. autoclass:: networkTree.ServerNode.ServerNode
   :members:   

Related Topics
--------------
.. toctree::
   ServerNetworkFactory
   OpStates
   
.. _pygraph: http://pygraphlib.sourceforge.net/doc/public/pygraphlib.pygraph.DGraph-class.html