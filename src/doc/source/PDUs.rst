Power distribution units (PDUs) - outlets
=========================================

PDUs are object generators that create outlets for a server.

When creating a new one you should extend the class :class:`outlets.OutletTemplate.OutletTemplate` . 

Here are the methods you should implement when writing a new PDU class:

.. autoclass:: outlets.OutletTemplate.OutletTemplate
   :members: _setOutletState, _getOuteletState, updateData