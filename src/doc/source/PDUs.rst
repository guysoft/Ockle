Power distribution units (PDUs) - Outlets
=========================================

PDUs are object generators that create outlets for a server.
Outlets represent a physical power socket that that can switch the server's power on or off. Outlet also have a ``data`` field that gets logged in the :doc:`PluginLogger`.

Coding a new PDU type
---------------------

When creating a new one you should extend the class :class:`outlets.OutletTemplate.OutletTemplate` . 

The python file containing the class should be placed in the ``src/outlets`` package.

Here are the methods you should implement when writing a new PDU class:

.. autoclass:: outlets.OutletTemplate.OutletTemplate
   :members: _setOutletState, _getOuteletState, updateData

Example Dummy Outlet
~~~~~~~~~~~~~~~~~~~~

Here is an example dummy outlet implementation 

.. code:: python

  from OutletTemplate import OutletTemplate

  class Dummy(OutletTemplate):
      ''' A dummy outlet, useful for testing
      '''
      def __init__(self,name,outletConfigDict={},outletParams={}):
	  OutletTemplate.__init__(self,name,outletConfigDict,outletParams)
	  self.setState(False)
	  return
      
      def _setOutletState(self,state):
	  self.state = state
	  return
      
      def updateState(self):
	  self.state=self._getOuteletState()
	  
      def _getOuteletState(self):
	  try:
	      self.state
	  except AttributeError:
	      self.state = False 
	  return self.state

Example for an outlet INI Template File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Here is an INI template file from the Raritan PDU, located at  ``src/config/conf_outlets/Raritan.ini``:

.. code:: python
  
  [pdu]
  pdu_ip=["string","192.168.0.1"]
  pdu_port=["int",161]
  read_community=["string","reading community name"]
  write_community=["string","writing community name"]
  agent_name=["string","Ockle"]

  [outletParams]
  socket=["intrange",1,"1-8"]