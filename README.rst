============================
YAFL: Yet Another Fake Login
============================

Welcome to another purposeless fake login web application. It is a useful way to
learn Flask and could in principle be used to collect credential from an hostile
entity who blindly injects credentials in this simple form.

How
===

It is a dummy html form which calls a POST against :code:`/login`, triggering a
function in `collector.py` that writes on a simple json file (default is
:code:`default_db.json`), using TinyDB python lib.

Run
===

CLI
----
You can use setuptools to install in a virtualenv all the dependencies

.. code:: bash

 $ virtualenv -p $(which python3) --no-site-packages venv
 $ . ./venv/bin/activate
 (venv)$ pip install .


You will find the `yafl` script in your PATH

.. code:: bash

 $ yafl --help
 Usage: yafl [OPTIONS]

 Options:
   -a, --address TEXT  Address to bind. Defaults to 127.0.0.1
   -p, --port INTEGER  Port to bind to. Defaults to 8081
   -l, --log TEXT      Path to log file. Defaults to ./default_db.json
   --help              Show this message and exit.

uwsgi+nginx
------------------

If you plan to run YAFL in production, I suggest to use uwsgi behind an nginx
instance. You can place the YAFL directory wherever it is practical to run it
for you and install the dipendencies systemwide.
You can use YAFL.ini to start uwsgi manually, but I suggest to use the systemd unit that comes with uwsgi. You have to place it in `/etc/uwsgi/YAFL.ini` and start uwsgi with

.. code:: bash

  $ sudo systemctl start uwsgi@YAFL

Then you can use the
following example to nginx, for example using the following and
placing it in `/etc/nginx/sites-available/yafl`

.. code::

 server {
    listen 80;
    server_name yafl.example.com;
    charset utf-8;

    location / { try_files $uri @yafl; }
    location @yafl{
        include uwsgi_params;
        uwsgi_pass unix:/tmp/yafl.sock;
    }
 }

and then symlinking

.. code:: bash

  $ sudo ln -s /etc/nginx/sites-available/yafl /etc/nginx/sites-enabled/yafl
  $ sudo systemctl start nginx


LICENCE
=======

This piece of code is released under the WTF Public Licence.
See :code:`LICENCE`

CREDITS
=======

The login html+css form is "Simple Login Form" from `colorlib.com`_
This code has been worked out partly during work ad Quantum Leap
(`quantumleap.it`_)


.. _`colorlib.com`: https://colorlib.com/wp/html5-and-css3-login-forms/
.. _`quantumleap.it`: https://www.quantumleap.it

