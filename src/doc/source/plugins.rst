Plugins
=======
.. note:: One of the main concept of Ockle's design is that everything that could be a plugin, should be.

Ockle allows to add major features by the use of plugins. Each plugin is python class instance that gets executed in its own thread, allowing the developer to add new logic and behavior. You should be able to write a plugin without modifying Ockle's core. But should be able to access any method within it.
Many core functions in Ockle are plugins themselves including the Automatic server control and the communication to the web-based GUI. 

In order to write a plugin, you should know that there are many pre-built tools that would help you in building one. Including a way to place your configuration variables in the GUI via simple `Plugin ini template files`_

A general description of the tools available for the plugin would look like this:

Plugin Framework Diagram
------------------------

.. image:: images/PluginTools.png
   :align: center
   :alt: What a plugin 'sees'

Every plugin is supplied with a pointer to the Main Daemon singletron, allowing access to services such as the server tree data-structure (to change the state of the servers) and the communication handler (which lets you add more commands to the communication with the webserver or any other external client).
The plugin also gets access to all the functions defined in the plugin template class, such as special functions that arrange the configuration variable storage.

The Template plugin Class
-------------------------
To use this plugin framework simple extend the :class:`plugins.ModuleTemplate.ModuleTemplate` . 
You may either extend the ``__init__`` function to do things with Ockle starts, or the ``run`` method that will run your code in a seprate thread with access to Ockle's functionality. You can also use the ``__init__`` function to register new commends to send to Ockle as done in :class:`plugins.CoreCommunicationCommands.CoreCommunicationCommands`.

.. autoclass:: plugins.ModuleTemplate.ModuleTemplate
   :members:

Example
~~~~~~~

Here is a simple plugin example, this plugin simply sends to debug "I am a test plugin" message every X seconds, as defined in its config var.


.. code:: python

  import time
  from plugins.ModuleTemplate import ModuleTemplate
  class TimerPluginExample(ModuleTemplate):
      ''' Example plugin that just sends to debug a message every X seconds, as defined in its config var
      '''
      
      def __init__(self,MainDaemon):
	  ModuleTemplate.__init__(self,MainDaemon)
	  self.wait_time = self.getConfigInt("WAIT_TIME")
	  
      def run(self):
	  while self.mainDaemon.running:
	      self.debug("I am a test plugin")
	      time.sleep(self.wait_time)

Plugin ini template files
-------------------------

If you want the configuration variable to be changeable at the webserver GUI, you must provide a template ini file in the ``src/config/plugins`` folder. The files should have the name of the plugin class proceeded with the .ini ending.

The section should be named ``plugins.<plugin name>`` .

These template files follow Ockle's :doc:`INITemplates` .

Example
~~~~~~~
Lets look at our ``TimerPluginExample`` example from before. We will need it to have a  ``src/config/plugins/TimerPluginExample.ini``. This file should contain the following text:

.. code:: python
  
  [plugins.TimerPluginExample]
  WAIT_TIME=["int",1]

With those two files in place Ockle takes it from here and the plugin would be available to the user in the config sections.