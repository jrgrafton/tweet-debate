unittest2 is a backport of the new features added to the unittest testing
framework in Python 2.7 and onwards. It is tested to run on Python 2.6, 2.7,
3.2, 3.3, 3.4 and pypy.

To use unittest2 instead of unittest simply replace ``import unittest`` with
``import unittest2``.

unittest2 is maintained in a mercurial repository. The issue tracker is on
google code:

* `unittest2 hg <http://hg.python.org/unittest2>`_
* `unittest2 issue tracker
  <http://code.google.com/p/unittest-ext/issues/list>`_
* `Article / Docs: New features in unittest
  <http://www.voidspace.org.uk/python/articles/unittest2.shtml>`_

Thanks to Mark Roddy, there is a distribution of unittest2 0.5.1 for Python 2.3.
This is maintained as a separate branch and is a separate download.

To avoid problems with ``pip`` installing the wrong distribution, the Python 2.3
version of unittest2 can't be hosted on PyPI:

* `Download unittest2 0.5.1 for Python 2.3 <http://voidspace.org.uk/downloads/unittest2-0.5.1-python2.3.zip>`_

There was a separate version of unittest2 for Python 3. This is no longer
needed, but still exists on PyPI. This had the project name "unittest2py3k" but
uses the same package name ("unittest2"):

* `unittest2 for Python 3 <http://pypi.python.org/pypi/unittest2py3k>`_

Classes in unittest2 derive from the appropriate classes in unittest, so it
should be possible to use the unittest2 test running infrastructure without
having to switch all your tests to using unittest2 immediately. Similarly
you can use the new assert methods on ``unittest2.TestCase`` with the standard
unittest test running infrastructure. Not all of the new features in unittest2
will work with the standard unittest test loaders, runners result objects
however.

In general for documentation on unittest2 see the current latest documented of
CPython:

* `CPython unittest documentation <https://docs.python.org/dev/library/unittest.html>`_

New features include:

* ``addCleanups`` - better resource management
* *many* new assert methods including better defaults for comparing lists,
  sets, dicts unicode strings etc and the ability to specify new default methods
  for comparing specific types
* ``assertRaises`` as context manager, with access to the exception afterwards
* test discovery and new command line options (including failfast and better
  handling of ctrl-C during test runs)
* class and module level fixtures: ``setUpClass``, ``tearDownClass``,
  ``setUpModule``, ``tearDownModule``
* test skipping and expected failures
* new ``delta`` keyword argument to ``assertAlmostEqual`` for more useful
  comparison and for comparing non-numeric objects (like datetimes)
* ``load_tests`` protocol for loading tests from modules or packages
* ``startTestRun`` and ``stopTestRun`` methods on TestResult
* various other API improvements and fixes

.. note:: Command line usage

    In Python 2.7 you invoke the unittest command line features (including test
    discover) with ``python -m unittest <args>``. As unittest is a package, and
    the ability to invoke packages with ``python -m ...`` is new in Python 2.7,
    we can't do this for unittest2.

    Instead unittest2 comes with a script ``unit2``.
    `Command line usage
    <http://docs.python.org/dev/library/unittest.html#command-line-interface>`_::

        unit2 discover
        unit2 -v test_module

    There is also a copy of this script called ``unit2.py``, useful for Windows
    which uses file-extensions rather than shebang lines to determine what
    program to execute files with. Both of these scripts are installed by
    distutils.

Until I write proper documentation, the best information on all the new features
is the development version of the Python documentation for Python 2.7:

* http://docs.python.org/dev/library/unittest.html

Look for notes about features added or changed in Python 2.7.

.. note::

    unittest2 is already in use for development of `distutils2
    <http://hg.python.org/distutils2>`_.

    Version 0.5.1 of unittest2 has feature parity with unittest_ in Python 2.7
    final. If you want to ensure that your tests run identically under unittest2
    and unittest in Python 2.7 you should use unittest2 0.5.1.

    Later versions of unittest2 include changes in unittest made in Python 3.2
    and onwards after the release of Python 2.7.


.. _unittest: http://docs.python.org/release/2.7/library/unittest.html


Differences
===========

Differences between unittest2 and unittest in Python 2.7:

``assertItemsEqual`` does not silence Py3k warnings as this uses
``warnings.catch_warnings()`` which is new in Python 2.6 (and is used as a
context manager which would be a pain to make work with Python 2.4).

``TestCase.longMessage`` defaults to True because it is better. It defaults to
False in Python 2.7 for backwards compatibility reasons.

``python -m package`` doesn't work in versions of Python before Python 2.7. The
command line features of unittest2 are provided by a ``unit2`` (and
``unit2.py``) script instead.

unittest2 includes a very basic setuptools compatible test collector. Specify
``test_suite = 'unittest2.collector'`` in your setup.py. This starts test
discovery with the default parameters from the directory containing setup.py, so
it is perhaps most useful as an example (see unittest2/collector.py).

In unittest2 TextTestResult.stopTestRun is responsible for calling printErrors.
This is desirable behaviour but in Python 3.1 TestResult.stopTestRun was
documented as being empty and subclasses shouldn't need to call it. This would
make the change backwards incompatible and needs thinking about.



Issues
======

A ``TestResult`` object with unexpected successes returns True
for ``result.wasSuccessful()``. Difficult to know if this is the correct
behaviour or not.

If a dotted path name is used for test discovery then a globally installed
module/package will still be used in preference of one in the current
directory. When doing discovery from a dotted path name we could check for this
specific case.

The ``removeHandler`` decorator could also be a context manager.

`Issue 8313: <http://bugs.python.org/issue8313>`_, \<unprintable AssertionError object\>
message in unittest tracebacks, is hard to fix in versions of Python before 2.7.
The fix in Python 2.7 relies on changes to both the traceback module and
traceback objects. As the issue is rare I am leaving it unfixed in unittest2.

There are several places in unittest2 (and unittest) that call ``str(...)`` on
exceptions to get the exception message. This can fail if the exception was
created with non-ascii unicode. This is rare and I won't address it unless it is
actually reported as a problem for someone.

A comparison of text or long sequences (using ``assertSequenceEqual`` or
``assertMultiLineEqual`` etc) can take a *long* time to generate diffs for
failure messages. These methods use ``prettyprint`` and ``difflib``.

``pip install -e .`` on Python3.2 in the unittest2 source will fail unless
setuptools > 0.6.24 is already installed. This is a combination of needing a
newer setuptools (to avoid the use of execfile) and setup_requires falling back
to easy_install that doesn't know how to upgrade setuptools just-in-time that
prevents it being fixed in unittest2.


CHANGELOG
=========

2015-06-20 - 1.1.0
------------------

- Issue #15836: assertRaises(), assertRaisesRegex(), assertWarns() and
  assertWarnsRegex() assertments now check the type of the first argument
  to prevent possible user error.  Based on patch by Daniel Wagner-Hall.

- Issue #24134: assertRaises(), assertRaisesRegex(), assertWarns() and
  assertWarnsRegex() checks now emits a deprecation warning when callable is
  None or keyword arguments except msg is passed in the context manager mode.

- Issue #22903: The fake test case created by unittest.loader when it fails
  importing a test module is now picklable.


2015-03-12 - 1.0.1
------------------

- Unittest2 issue #94: Need at least 1.4 of six.

2015-03-06 - 1.0.0
------------------

- Issue #22936: Permit showing local variables in tracebacks.

2014/11/05 - 0.8
----------------

- Issue #22457: Honour load_tests in the start_dir of discovery.

- Issue #22894: TestCase.subTest() would cause the test suite to be stopped
  when in failfast mode, even in the absence of failures.

2014/10/31 - 0.7.1
------------------

Fix for 0.7.0 being broken. Also switches from both manual and entrypoint
scripts to just entrypoint scripts to reduce the possibility of similar
oversights in future.

2014/10/31 - 0.7.0
------------------

This release contains backports from cPython 3.5 of all (I think) commits since
2010, as of today.

2014/10/28 - 0.6.0
------------------

Many thanks to Mark Roddy and Ezio Melotti who contributed substantially to
this release.

* Changed supported Python versions to start at 2.6, and include all released 3.x
  and pypy. (Robert Collins)
* Invoking `unit2` without args starts test discovery
* Added `TestCase.assertWarns` and `TestCase.assertWarnsRegexp` context managers
* Fix Python issue 9926. TestSuite subclasses that override __call__ are called
  correctly.
* Removed unused `maxDiff` parameter from `TestCase.assertSequenceEqual`.
* DeprecationWarning for unsupported result objects (missing addSkip method)
  became RuntimeWarning.
* Addition of `TestCase.assertWarns` as a context manager.


2010/07/12 - 0.5.1
------------------

Reverted script names created by setuptools back to "unit2" instead of
"unit2.py". (Not necessary as setuptools creates stub .exes for console scripts
anyway.)


2010/07/11 - 0.5.0
------------------

Addition of a setuptools compatible test collector (very basic). Specify
``test_suite = 'unittest2.collector'`` in your setup.py.

``TestSuite.debug()`` and ``TestCase.debug()`` now execute cleanup functions
and class and module level setups and teardowns.

No longer monkey-patch os.path.relpath for Python 2.4 / 2.5 so that projects
don't accidentally depend on our patching. Contributed by Konrad Delong.

Added a Python version specific unit2 entrypoint. This will, for example,
create a ``unit2-2.6`` script if unittest2 is installed with Python 2.6.
(Requires setuptools or distribute.)

Python 2.3 compatibility (in the python2.3 branch of the repository),
contributed by Mark Roddy.

setuptools console script entry points are created as '.py' scripts on Windows.

Feature parity with the Python 2.7 final release.


2010/06/06 - 0.4.2
------------------

Improved help message for ``unit2 discover -h``.

SkipTest in unittest.TestCase.setUpClass or setUpModule is now reported as a
skip rather than an error.

Excessively large diffs due to ``TestCase.assertSequenceEqual`` are no
longer included in failure reports. (Controlled by ``TestCase.maxDiff``.)

Matching files during test discovery is done in ``TestLoader._match_path``. This
method can be overriden in subclasses to, for example, match on the full file
path or use regular expressions for matching.

Addition of a setuptools compatible entrypoint for the unit2 test runner script.
Contributed by Chris Withers.

Tests fixed to be compatible with Python 2.7, where deprecation warnings are
silenced by default.

Feature parity with unittest in Python 2.7 RC 1.


2010/05/09 - 0.4.1
------------------

If test discovery imports a module from the wrong location (usually because the
module is globally installed and the user is expecting to run tests against a
development version in a different location) then discovery halts with an
``ImportError`` and the problem is reported.

Added docstrings to ``assertRegexpMatches`` and ``assertNotRegexpMatches``.

Putting functions in test suites no longer crashes.

Feature parity with unittest in Python 2.7 Beta 2.

2010/04/08 - 0.4.0
------------------

Addition of ``removeHandler`` for removing the control-C handler.

``delta`` keyword argument for ``assertAlmostEqual`` and
``assertNotAlmostEqual``.

Addition of -b command line option (and ``TestResult.buffer``) for buffering
stdout / stderr during test runs.

Addition of ``TestCase.assertNotRegexpMatches``.

Allow test discovery using dotted module names instead of a path.

All imports requiring the signal module are now optional, for compatiblity
with IronPython (or other platforms without this module).

Tests fixed to be compatible with nosetest.


2010/03/26 - 0.3.0
------------------

``assertSameElements`` removed and ``assertItemsEqual`` added; assert that
sequences contain the same elements.

Addition of -f/--failfast command line option, stopping test run on first
failure or error.

Addition of -c/--catch command line option for better control-C handling during
test runs.

Added ``BaseTestSuite``, for use by frameworks that don't want to support shared
class and module fixtures.

Skipped test methods no longer have ``setUp`` and ``tearDown`` called around
them.

Faulty ``load_tests`` functions no longer halt test discovery.

Using non-strings for failure messages now works.

Potential for ``UnicodeDecodeError`` whilst creating failure messages fixed.

Split out monolithic test module into a package.

BUGFIX: Correct usage message now shown for unit2 scripts.

BUGFIX: ``__unittest`` in module globals trims frames from that module in
reported stacktraces.


2010/03/06 - 0.2.0
------------------

The ``TextTestRunner`` is now compatible with old result objects and standard
(non-TextTestResult) ``TestResult`` objects.

``setUpClass`` / ``tearDownClass`` / ``setUpModule`` / ``tearDownModule`` added.


2010/02/22 - 0.1.6
------------------

Fix for compatibility with old ``TestResult`` objects. New tests can now be run
with nosetests (with a DeprecationWarning for ``TestResult`` objects without
methods to support skipping etc).


0.1
---

Initial release.


TODO
====

* Document ``SkipTest``, ``BaseTestSuite```

Release process
===============

1. Make sure there is an entry in the Changelog in this document.
1. Update __version__ in unittest2/__init__.py
1. Commit.
1. Create a tag for the version (e.g. ``hg tag 0.6.0``)
1. Push so there is no outstanding patches and no room for races.
1. Run ``make release`` to build an sdist and wheel and upload to pypi.


