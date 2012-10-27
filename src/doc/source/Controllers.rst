Controllers - Controls
======================

Controllers are object generators that create controls for a server.
Controls are a set of commands that can tell a server to switch itself off on the software level (before the outlets switch off its power). Controllers also have a ``data`` field that gets logged in the :doc:`PluginLogger`, enabling logging information from the servers.

Coding a New Controller Type
-----------------------------
When creating a new controller type you should extend the class :class:`controller.ControllerTemplate.ControllerTemplate`. 

The python file containing the class should be placed in the ``src/controllers`` package.

Here are the methods you should implement when writing a new Controller class:

.. autoclass:: controllers.ControllerTemplate.ControllerTemplate
   :members: _setControlState, _getControlState, updateData

Example Dummy Control
~~~~~~~~~~~~~~~~~~~~~

Here is an example dummy outlet implementation 

.. code:: python

  from controllers.ControllerTemplate import ControllerTemplate

  class Dummy(ControllerTemplate):
      def __init__(self,name,controllerConfigDict={},controllerParams={}):
	  ControllerTemplate.__init__(self,name,controllerConfigDict={},controllerParams={})
	  self.setState(True)
	  return
      
      def updateData(self):
	  pass
      
      def _setControlState(self,state):
	  self.state=True
	  return True
      
      def _getControlState(self):
	  try:
	      return self.state
	  except:
	      self.state = True #init
	      return False

Example for a control INI Template File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Here is an INI template file from a control to send ssh commands to a server, located at  ``src/config/conf_controllers/SSHController.ini``:

.. code:: python
  
  [controller]

  [controlParams]
  host=["string","localhost"]
  username=["string","root"]
  password=["string",""]
  key_filename=["string",""]
  timeout=["int",21]
  allow_agent=["bool",true]
  look_for_keys=["bool",true]
  compress=["bool",true]