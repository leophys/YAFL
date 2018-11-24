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

Mailer
------

It is also possible to be warned of a first login attempt via email. There is a
``Mailer`` class in ``mailer.py`` done for this purpose. You will need an account
on a working SMTP relay. This usually consists of some information:

    - The SMTP relay address (usually the MX record associated to the domain
      of your email)[no default]
    - The port where to contact your SMTP relay (usually ``25``, ``465`` or ``587``)
      [default: ``25``]
    - Your mail account name (it can be your email address, or the fragment before ``@``)
      [no default]
    - Your password [no default]
    - Whether to ``STARTTLS`` after a successful connection to the mailserver (usually you
      need to set this to ``true`` if you use ``25`` or ``587``  as SMTP port)
      [default: ``false``]

Run
===

CLI
----
You can use setuptools to install in a virtualenv all the dependencies

.. code:: bash

 $ python3 -m venv venv
 $ . ./venv/bin/activate
 (venv)$ pip install .


You will find the `yafl` script in your PATH

.. code:: bash

 $ yafl --help

 Usage: yafl [OPTIONS]

   Command line entry point.

 Options:
   -a, --address TEXT      Address to bind. If no configuration given, defaults
                           to 127.0.0.1
   -p, --port INTEGER      Port to bind to. If no configuration given, defaults
                           to 8081
   -o, --output PATH       Path to log file. If no configuration given,
                           defaults to /tmp/yafl_<current_time>.json
   -m, --mailserver TEXT   The url to of the mailserver (should be the MX
                           record of your mail domain). If missing, the mailer
                           is disabled.
   -r, --mailport INTEGER  The port to use to connect to the mailserver. Errors
                           if -m/--mailserver is missing.
   -u, --username TEXT     The username to use to log onto your SMTP relay.
                           Errors if -m/--mailserver is missing.
   -w, --password TEXT     The password to use to log onto your SMTP relay.
                           Errors if -m/--mailserver is missing.
                           DANGEROUS! May
                           persist in the shell history! Use the configuration
                           file instead!
   -f, --fromfield TEXT    Sets the From: in the mail sent. Errors if
                           -m/--mailserver is missing.
   -t, --tofield TEXT      Sets the To: in the mail sent. MANDATORY. Errors if
                           -m/--mailserver is missing.
   -s, --starttls BOOLEAN  Use STARTTLS connecting to the mailserver. Errors if
                           -m/--mailserver is missing.
   -c, --config FILENAME   Path to a configuration file. If given, bypasses all
                           the YAFL configuration hierarchy. Wants to be alone.
                           Fails if other options are given.
   --debug / --no-debug    Toggles debug (verbose output)
   --help                  Show this message and exit.




uwsgi+nginx
-----------

If you plan to run YAFL in production, I suggest to use uWSGI behind an nginx
instance. You can place the YAFL directory wherever it is practical to run it
for you and install the dependencies systemwide.

.. code:: bash

    $ cd path/to/yafl
    $ sudo pip install .

You can use ``utils/uwsgi/YAFL_emperor.yaml`` to start uWSGI manually in emperor mode
(but I suggest to use a systemd unit), placing ``utils/uwsgi/uwsgi.d/yafl_app.yaml``
in ``/etc/uwsgi.d/``.
Then you can use the following example to nginx, for example using the following and
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


Development with docker-compose
-------------------------------

I use docker a lot. This project ships also a ``docker-compose.yaml`` file to be used with
to develop locally. Just

.. code:: bash

    $ docker-compose build
    $ docker-compose up

And you should find the app exposed on ``localhost``. Be aware that port 80 on localhost must
not be used by another program.
The app is mounted and installed inside the docker container. Therefore, you may develop and see
the changes in real time.
There is also an auxiliary ``docker-compose.debug.yml``. It forces the app in debug mode
(via the ``YAFL_APP_LOG_LEVEL=DEBUG`` environment variable) and mounts on the container
``utils/yafl.yaml``. You can customize the way the app runs via this file. To have a hint,
look at ``utils/yafl.yaml.example``.


Configuration
=============

``YAFL`` is not yet very customizable. It follows a strict order in its configuration logic:

    - First reads from the environment variables
    - Then from a configuration file
    - Then uses the default

First, let's take a look at an example configuration file:

.. code:: yml
 ---
 app:
     db_path: '/tmp/yafl_example.json'
     log_level: 'DEBUG'
     address: 1.3.1.2
     port: 8666
 mail:
     address: 'mail.example.com'
     username: 'me@example.com'
     password: 'password!'
     from_field: 'yafl@example.com'
     to_field: 'other.me@sample.net'
     starttls: true

These are all the configurations accepted by ``YAFL``, divided in two sections
(``app`` and ``mail``).

Environment variables
---------------------

``YAFL`` looks first for environment variables of the form: ``YAFL_<section>_<conf_key>``
(all upper case).

Configuration file
------------------

``YAFL`` accepts only ``.yaml`` or ``.yml`` files, and looks in a set of predetermined
paths in the following order:

 - ``$PWD/.yafl.yaml``
 - ``$PWD/.yafl.yml``
 - ``~/.yafl.yaml``
 - ``~/.yafl.yml``
 - ``/etc/yafl.yaml``
 - ``/etc/yafl.yml``

If none of the following is present, is looks for a path in the ``YAFL_CONF_FILE`` environment
variable.

Defaults
--------

``YAFL`` has the following default values (``_NOW`` expands to the current time):

.. code:: python

 DEFAULT_APP_CONF = {
     'db_path': '/tmp/yafl_%s.json' % _NOW,
     'log_level': logging.INFO,
     'address': '127.0.0.1',
     'port': 8081,
 }


 DEFAULT_MAIL_CONF = {
     'address': None,
     'port': 25,
     'username': None,
     'password': None,
     'from_field': None,
     'to_field': None,
     'starttls': None,
 }


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

