Communication Handler 
=====================

The communication handler is a class that stores all the commands Ockle can handle from an external client. There is one instance of this class on the whole program and it is used to add new commands all over Ockle (both core and plugins).

A communication plugin (such as the SocketListner plugin) is then used to handle an incoming command.

A command consists of a command name and a data dict. A reply is either the same command with a dataDict holding the reply, or a command with the name "Unknown Command" if the communication Handler does not recognize the request.

The class that builds a message to be sent over a communication plugin is the Message class, located in CommunicationMessage module. It should not really be used directly since only the communication handler and a single function in :doc:`OckleClient`.

Communication Handler Class
---------------------------
.. autoclass:: common.CommunicationHandler.CommunicationHandler
   :members:
