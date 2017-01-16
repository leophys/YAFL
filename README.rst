==============================
YAFL: Yet Another Fake Login
==============================

Welcome to another purposeless fake login web application. It is a useful way to
learn Flask and could in principle be used to collect credential from an hostile
entity who blindly injects credentials in this simple form.

How
===

It is a dummy html form which calls a POST against :code:`/login`, triggering a
function in collector.py that writes on a simple json file (default is
:code:`default_db.json`), using TinyDB python lib.

Install
-------

I plan to write a :code:`setup.py`, meanwhile read the install.txt file, which
contains the prerequisites (:code:`pip install <package>`, python 3 compliant).

Run
---

I plan to wrap it behind a uwsgi+nginx instance, meanwhile you could run it
with

    .. code-block:: bash

       $ python collector.py


LICENCE
=======

This piece of code is released under the WTF Public Licence.
See :code:`LICENCE`

CREDITS
=======

The login html+css form is "Simple Login Form" from `colorlib.com`_
This code has been worked out partly during work at Quantum Leap
(`quantumleap.it`_)


.. _`colorlib.com`: https://colorlib.com/wp/html5-and-css3-login-forms/
.. _`quantumleap.it`: https://www.quantumleap.it
