The Communication Client
========================

The communication is a python library that lets you send commands to Ockle from a python shell using an external program.

.. automodule:: ockle_client.ClientCalls
   :members: 


Example usage
-------------
 Here is a simple example on how to use the ockle_client module:

.. code-block:: python

  import webserver.ockle_client.ClientCalls as ockleClient
  ockleClient.PORT = 8088
  ockleClient.OCKLE_SERVER_HOSTNAME = 'localhost'

  print ockleClient.listCommands()
