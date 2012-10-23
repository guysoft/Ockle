Installing Ockle
================

.. note:: It is recommended to run Ockle in a virtualenv. This is to upgrades of the system won't break your control over the servers. So first make sure you have it.

- Installing virtualenv:
.. code-block:: bash

    apt-get install python-virtualenv


Set up the python environment
-----------------------------

- In order to compile some of the python module you will need to install the following packages (or your distro's equivelent)
.. code-block:: bash

  apt-get install libxslt1-dev libxml2-dev libgraphviz-dev

- Run the following commands to get a python environment with the correct versions of software. (you can change *~/pythonenv* to any path that suits you ):

.. code-block:: bash

  python2.7 /usr/bin/virtualenv ~/pythonenv
  ~/pythonenv/bin/easy_install pyramid==1.2.7
  mkdir ~/pythonenv/downloads/
  cd ~/pythonenv/downloads/
  svn checkout http://networkx.lanl.gov/svn/pygraphviz/trunk pygraphviz
  ~/pythonenv/bin/easy_install waitress
  ~/pythonenv/bin/easy_install WebError
  ~/pythonenv/bin/easy_install pyramid-handlers
  ~/pythonenv/bin/easy_install pyramid-beaker
  ~/pythonenv/bin/easy_install pyramid_debugtoolbar
  ~/pythonenv/bin/easy_install psycopg2
  ~/pythonenv/bin/easy_install pycrypto
  ~/pythonenv/bin/easy_install SQLAlchemy
  ~/pythonenv/bin/easy_install lxml
  ~/pythonenv/bin/easy_install paramiko

- Edit the setup.py file ~/pythonenv/downloads/pygraphviz/setup.py
and add replace the following lines:

.. code-block:: python

  library_path='/usr/lib/graphviz/'
  include_path='/usr/include/graphviz/'

Then run:
.. code-block:: bash

  ~/pythonenv/bin/python setup.py install

Installing Ockle's GUI
----------------------

Ockle's web-based GUI uses Pyramid_, a python-based web development framework.
You can either deploy a pyramid app on a apache/nginx webserver, or you can run it on a standalone webserver.
To run it on a standalone webserer you can run the supplied script:

.. code-block:: bash

  ~/pythonenv/bin/python src/webserer/application.py

.. note:: Currently if the GUI can't communicate with Ockle an error message is displayed. If this happens to you follow your server's error log to see why the communication has failed.

.. note:: The standalone webserver loads by default on `port 8000 <http://localhost:8000>`_ .

How to set up
-------------
- Copy config.ini.example to config.ini

Once the file is copied Ockle should be able to run. You can tweak the config.ini file manually or use the webserver GUI which should.


How to run
----------

To run the Ockle simply exacute:

.. code-block:: bash

  ~/pythonenv/bin/python src/MainDaemon.py



.. _Pyramid: http://www.pylonsproject.org/projects/pyramid/

