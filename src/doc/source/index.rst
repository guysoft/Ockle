.. Ockle documentation master file, created by
   sphinx-quickstart on Tue Oct 23 00:50:37 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Ockle's documentation!
=================================
.. image:: images/Logo.png
   :align: right
   :alt: Ockle

Ockle is a tool which lets you control a group of power distribution units (PDUs_) and the servers which connected to them.
Servers can be dependent on each other, and Ockle can then determine which servers should be turned on according to those dependencies. After server is turned on Ockle can run automated tests to make sure they indeed provide the services that are required by the servers.

Design principles in Ockle
--------------------------
- *Extensibility* – I tried to implement the method “everything is a plugin”, by this I mean that every new form of logic or functionally could be added and removed from the configuration without changing the code itself. Every new feature would go in to its own module and process thread.
- *Lightweight* – Ockle is split to a control daemon and a webserver, so the device controlling the servers could be put on a embedded device on a separate power supply.
- *Easy to use* – The webserver aims to give an intuitive user experience, with helpful information about the server's health and power usage status.

Where to get Ockle
------------------

Ockle is available at GitHub_.

You can download it by cloning it:

.. code-block:: bash

  git clone https://github.com/guysoft/Ockle.git

Ockle is Free Software
~~~~~~~~~~~~~~~~~~~~~~

This software is distributed under the `GNU General Public License, version 2 <https://www.gnu.org/licenses/gpl-2.0.html>`_
 
User Manual
===========

.. toctree::
   InstallingOckle
   WebserverUser
   UsingOckle

Developer Manual
================

.. toctree::
   core
   plugins
   Webserver
   OckleClient
   ServerObjects
   INITemplates
   :maxdepth: 4

Libraries used (learned?)
-------------------------

- `pyGraph <http://pygraphlib.sourceforge.net>`_ – python graph data structure
- `PyDot <https://code.google.com/p/pydot>`_ library / xDot format
- `SQLAlchemy <http://www.sqlalchemy.org>`_ – cross-platform databas
- `Pyramid <http://www.pylonsproject.org/>`_ – Webserver framework
- `Chameleon <http://chameleon.repoze.org/>`_ template engine
- `Graphviz <http://www.graphviz.org/>`_ / `Canviz <https://code.google.com/p/canviz/>`_ – Graph visualization libraries
- `JqPlot <http://www.jqplot.com>`_ - a plotting and charting plugin for the jQuery Javascript framework
- `PySNMP <http://sourceforge.net/projects/pysnmp>`_ – Communication with the Raritan Dominion PX Remote Power Control
- `straight.plugin <https://github.com/ironfroggy/straight.plugin>`_ – A plugin loading facility 
- `Socket <http://docs.python.org/library/socket.html>`_ (python standard library class) - Low-level networking interface
- `prototype.js <http://prototypejs.org>`_ - The main page requires prototype for Canvoiz to work
- `sphinx <http://sphinx.pocoo.org>`_ - Documentation

Project
=======
.. toctree::
   FutureWork
   :maxdepth: 3

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _GitHub: https://github.com/guysoft/Ockle
.. _PDUs: https://en.wikipedia.org/wiki/Power_distribution_unit

.. _Pygraph: http://pygraphlib.sourceforge.net
