Webserver - Ockle's GUI
=======================

Ockle's GUI is a `pyramid 1.2 <http://docs.pylonsproject.org/projects/pyramid/en/1.2-branch/index.html/>`_ application that communicates to the Ockle Daemon.

There are a few helper functions for the view's page


Helper fuctions for generating multi-choice config pages
--------------------------------------------------------

When creating config pages with multi choice fields, you *must* populate the ``multiListChoices`` variable and pass it to the template, this can be done using the :mod:`views.multiChoiceGenerators` module:

.. automodule:: views.multiChoiceGenerators
   :members:
   :private-members:
