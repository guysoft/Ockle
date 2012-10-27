Operation States (OpStates)
===========================

All objects in :doc:`networkTree` keep Operation States of their objects they represent. By tracking the states its easy to find out what component is faulty in the server network.

Server/Outlet/control OpStates
------------------------------
.. autoclass:: common.common.OpState
   :members:

   .. autoattribute:: common.common.OpState

Test OpStates
-------------
.. autoclass:: testers.TemplateTester.TesterOpState
   :members:

   .. autoattribute:: testers.TemplateTester.TesterOpState