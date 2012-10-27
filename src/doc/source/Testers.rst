Testers - Tests
===============

Testers are object generators that create tests for a server.
Tests are a set of commands that runs after a server has been switched on, to make sure its serving the network correctly.

Coding a New Tester Type
-----------------------------
When creating a new tester type you should extend the class :class:`testers.TemplateTester.TemplateTester`. 

The python file containing the class should be placed in the ``src/testers`` package.

Here is the methods you should implement when writing a new Tester class:

.. autoclass:: testers.TemplateTester.TemplateTester
   :members: _test

Example Dummy Tester
~~~~~~~~~~~~~~~~~~~~~

Here is an example dummy outlet implementation 

.. code:: python

  from TemplateTester import TemplateTester
  import json

  class Dummy(TemplateTester):
      ''' A simple ping test
      '''
      def __init__(self,name,testerConfigDict={},testerParams={}):
	  TemplateTester.__init__(self,name, testerConfigDict, testerParams)
	  self.state = json.loads(testerParams["succeed"])
	  return
      
      def _test(self):
	  '''Runs the test
	  
	  :return: Return True if succeeded
	  '''
	  return self.state

Example for a control INI Template File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Here is an INI template file from the dummy test above, which is placed in  ``src/config/conf_testers/SSHController.ini``:

.. code:: python
  
  [tester]

  [testParams]
  succeed=["bool", true]