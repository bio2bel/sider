Bio2BEL SIDER |build| |coverage| |documentation|
================================================
Converts the Side Effect Resource (SIDER) to BEL.

Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
``bio2bel_sider`` can be installed easily from `PyPI <https://pypi.python.org/pypi/bio2bel_sider>`_ with
the following code in your favorite terminal:

.. code-block:: sh

    $ python3 -m pip install bio2bel_sider

or from the latest code on `GitHub <https://github.com/bio2bel/sider>`_ with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/bio2bel/sider.git@master

Setup
-----
SIDER can be downloaded and populated from either the Python REPL or the automatically installed command line
utility.

Python REPL
~~~~~~~~~~~
.. code-block:: python

    >>> import bio2bel_sider
    >>> sider_manager = bio2bel_sider.Manager()
    >>> sider_manager.populate()

Command Line Utility
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    bio2bel_sider populate

Citations
---------
- Kuhn, M., *et al.* (2016). `The SIDER database of drugs and side effects <https://doi.org/10.1093/nar/gkv1075>`_. Nucleic Acids Research, 44(D1), D1075–D1079.

.. |build| image:: https://travis-ci.org/bio2bel/sider.svg?branch=master
    :target: https://travis-ci.org/bio2bel/sider
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/bio2bel/sider/coverage.svg?branch=master
    :target: https://codecov.io/gh/bio2bel/sider?branch=master
    :alt: Coverage Status

.. |documentation| image:: http://readthedocs.org/projects/bio2bel-interpro/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/sider/en/latest/?badge=latest
    :alt: Documentation Status

.. |climate| image:: https://codeclimate.com/github/bio2bel/sider/badges/gpa.svg
    :target: https://codeclimate.com/github/bio2bel/sider
    :alt: Code Climate

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/bio2bel_sider.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/bio2bel_sider.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/bio2bel_sider.svg
    :alt: MIT License
