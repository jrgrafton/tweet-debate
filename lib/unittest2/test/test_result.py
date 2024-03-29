import sys
import textwrap
import traceback2 as traceback

import six
from six.moves import StringIO

import unittest2
import unittest2 as unittest


class MockTraceback(object):
    class TracebackException:
        def __init__(self, *args, **kwargs):
            self.capture_locals = kwargs.get('capture_locals', False)
        def format(self):
            result = ['A traceback']
            if self.capture_locals:
                result.append('locals')
            return result

def restore_traceback():
    unittest.result.traceback = traceback


class Test_TestResult(unittest2.TestCase):
    # Note: there are not separate tests for TestResult.wasSuccessful(),
    # TestResult.errors, TestResult.failures, TestResult.testsRun or
    # TestResult.shouldStop because these only have meaning in terms of
    # other TestResult methods.
    #
    # Accordingly, tests for the aforenamed attributes are incorporated
    # in with the tests for the defining methods.
    ################################################################

    def test_init(self):
        result = unittest2.TestResult()

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(result.shouldStop, False)
        self.assertIsNone(result._stdout_buffer)
        self.assertIsNone(result._stderr_buffer)

    # "This method can be called to signal that the set of tests being
    # run should be aborted by setting the TestResult's shouldStop
    # attribute to True."
    def test_stop(self):
        result = unittest2.TestResult()

        result.stop()

        self.assertEqual(result.shouldStop, True)

    # "Called when the test case test is about to be run. The default
    # implementation simply increments the instance's testsRun counter."
    def test_startTest(self):
        class Foo(unittest2.TestCase):
            def test_1(self):
                pass

        test = Foo('test_1')

        result = unittest2.TestResult()

        result.startTest(test)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        result.stopTest(test)

    # "Called after the test case test has been executed, regardless of
    # the outcome. The default implementation does nothing."
    def test_stopTest(self):
        class Foo(unittest2.TestCase):
            def test_1(self):
                pass

        test = Foo('test_1')

        result = unittest2.TestResult()

        result.startTest(test)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        result.stopTest(test)

        # Same tests as above; make sure nothing has changed
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

    # "Called before and after tests are run. The default implementation does nothing."
    def test_startTestRun_stopTestRun(self):
        result = unittest2.TestResult()
        result.startTestRun()
        result.stopTestRun()

    # "addSuccess(test)"
    # ...
    # "Called when the test case test succeeds"
    # ...
    # "wasSuccessful() - Returns True if all tests run so far have passed,
    # otherwise returns False"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test which raised an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() or TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    def test_addSuccess(self):
        class Foo(unittest2.TestCase):
            def test_1(self):
                pass

        test = Foo('test_1')

        result = unittest2.TestResult()

        result.startTest(test)
        result.addSuccess(test)
        result.stopTest(test)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

    # "addFailure(test, err)"
    # ...
    # "Called when the test case test signals a failure. err is a tuple of
    # the form returned by sys.exc_info(): (type, value, traceback)"
    # ...
    # "wasSuccessful() - Returns True if all tests run so far have passed,
    # otherwise returns False"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test which raised an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() or TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    def test_addFailure(self):
        class Foo(unittest2.TestCase):
            def test_1(self):
                pass

        test = Foo('test_1')
        try:
            test.fail("foo")
        except:
            exc_info_tuple = sys.exc_info()

        result = unittest2.TestResult()

        result.startTest(test)
        result.addFailure(test, exc_info_tuple)
        result.stopTest(test)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        test_case, formatted_exc = result.failures[0]
        self.assertIs(test_case, test)
        self.assertIsInstance(formatted_exc, six.string_types)

    # "addError(test, err)"
    # ...
    # "Called when the test case test raises an unexpected exception err
    # is a tuple of the form returned by sys.exc_info():
    # (type, value, traceback)"
    # ...
    # "wasSuccessful() - Returns True if all tests run so far have passed,
    # otherwise returns False"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test which raised an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() or TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    def test_addError(self):
        class Foo(unittest2.TestCase):
            def test_1(self):
                pass

        test = Foo('test_1')
        try:
            raise TypeError()
        except:
            exc_info_tuple = sys.exc_info()

        result = unittest2.TestResult()

        result.startTest(test)
        result.addError(test, exc_info_tuple)
        result.stopTest(test)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        test_case, formatted_exc = result.errors[0]
        self.assertIs(test_case, test)
        self.assertIsInstance(formatted_exc, six.string_types)

    def test_addError_locals(self):
        class Foo(unittest.TestCase):
            def test_1(self):
                1/0

        test = Foo('test_1')
        result = unittest.TestResult()
        result.tb_locals = True

        unittest.result.traceback = MockTraceback
        self.addCleanup(restore_traceback)
        result.startTestRun()
        test.run(result)
        result.stopTestRun()

        self.assertEqual(len(result.errors), 1)
        test_case, formatted_exc = result.errors[0]
        self.assertEqual('A tracebacklocals', formatted_exc)

    def test_addSubTest(self):
        log = []
        class Foo(unittest.TestCase):
            def test_1(self):
                with self.subTest(foo=1):
                    subtest = self._subtest
                    log.append(subtest)
                    try:
                        1/0
                    except ZeroDivisionError:
                        exc_info_tuple = sys.exc_info()
                    # Register an error by hand (to check the API)
                    result.addSubTest(test, subtest, exc_info_tuple)
                    # Now trigger a failure
                    self.fail("some recognizable failure")

        test = Foo('test_1')
        result = unittest.TestResult()

        test.run(result)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        test_case, formatted_exc = result.errors[0]
        subtest = log[0]
        self.assertIs(test_case, subtest)
        self.assertIn("ZeroDivisionError", formatted_exc)
        test_case, formatted_exc = result.failures[0]
        self.assertIs(test_case, subtest)
        self.assertIn("some recognizable failure", formatted_exc)

    def testGetDescriptionWithoutDocstring(self):
        result = unittest2.TextTestResult(None, True, 1)
        self.assertEqual(
                result.getDescription(self),
                'testGetDescriptionWithoutDocstring (' + __name__ +
                '.Test_TestResult)')

    def testGetSubTestDescriptionWithoutDocstring(self):
        with self.subTest(foo=1, bar=2):
            result = unittest.TextTestResult(None, True, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstring (' + __name__ +
                    '.Test_TestResult) (bar=2, foo=1)')
        with self.subTest('some message'):
            result = unittest.TextTestResult(None, True, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstring (' + __name__ +
                    '.Test_TestResult) [some message]')

    def testGetSubTestDescriptionWithoutDocstringAndParams(self):
        with self.subTest():
            result = unittest.TextTestResult(None, True, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstringAndParams '
                    '(' + __name__ + '.Test_TestResult) (<subtest>)')

    def testGetNestedSubTestDescriptionWithoutDocstring(self):
        with self.subTest(foo=1):
            with self.subTest(bar=2):
                result = unittest.TextTestResult(None, True, 1)
                self.assertEqual(
                        result.getDescription(self._subtest),
                        'testGetNestedSubTestDescriptionWithoutDocstring '
                        '(' + __name__ + '.Test_TestResult) (bar=2, foo=1)')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    def testGetDescriptionWithOneLineDocstring(self):
        """Tests getDescription() for a method with a docstring."""
        result = unittest2.TextTestResult(None, True, 1)
        self.assertEqual(
                result.getDescription(self),
               ('testGetDescriptionWithOneLineDocstring '
                '(' + __name__ + '.Test_TestResult)\n'
                'Tests getDescription() for a method with a docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    def testGetSubTestDescriptionWithOneLineDocstring(self):
        """Tests getDescription() for a method with a docstring."""
        result = unittest.TextTestResult(None, True, 1)
        with self.subTest(foo=1, bar=2):
            self.assertEqual(
                result.getDescription(self._subtest),
               ('testGetSubTestDescriptionWithOneLineDocstring '
                '(' + __name__ + '.Test_TestResult) (bar=2, foo=1)\n'
                'Tests getDescription() for a method with a docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    def testGetDescriptionWithMultiLineDocstring(self):
        """Tests getDescription() for a method with a longer docstring.
        The second line of the docstring.
        """
        result = unittest2.TextTestResult(None, True, 1)
        self.assertEqual(
                result.getDescription(self),
               ('testGetDescriptionWithMultiLineDocstring '
                '(' + __name__ + '.Test_TestResult)\n'
                'Tests getDescription() for a method with a longer '
                'docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    def testGetSubTestDescriptionWithMultiLineDocstring(self):
        """Tests getDescription() for a method with a longer docstring.
        The second line of the docstring.
        """
        result = unittest.TextTestResult(None, True, 1)
        with self.subTest(foo=1, bar=2):
            self.assertEqual(
                result.getDescription(self._subtest),
               ('testGetSubTestDescriptionWithMultiLineDocstring '
                '(' + __name__ + '.Test_TestResult) (bar=2, foo=1)\n'
                'Tests getDescription() for a method with a longer '
                'docstring.'))

    def testStackFrameTrimming(self):
        class Frame(object):
            class tb_frame(object):
                f_globals = {}
        result = unittest2.TestResult()
        self.assertFalse(result._is_relevant_tb_level(Frame))

        Frame.tb_frame.f_globals['__unittest'] = True
        self.assertTrue(result._is_relevant_tb_level(Frame))

    def testFailFast(self):
        result = unittest2.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = True
        result.addError(None, None)
        self.assertTrue(result.shouldStop)

        result = unittest2.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = True
        result.addFailure(None, None)
        self.assertTrue(result.shouldStop)

        result = unittest2.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = True
        result.addUnexpectedSuccess(None)
        self.assertTrue(result.shouldStop)

    def testFailFastSetByRunner(self):
        runner = unittest2.TextTestRunner(stream=StringIO(), failfast=True)
        self.testRan = False
        def test(result):
            self.testRan = True
            self.assertTrue(result.failfast)
        runner.run(test)
        self.assertTrue(self.testRan)


class TestOutputBuffering(unittest2.TestCase):

    def setUp(self):
        self._real_out = sys.stdout
        self._real_err = sys.stderr

    def tearDown(self):
        sys.stdout = self._real_out
        sys.stderr = self._real_err

    def testBufferOutputOff(self):
        real_out = self._real_out
        real_err = self._real_err

        result = unittest2.TestResult()
        self.assertFalse(result.buffer)

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

        result.startTest(self)

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

    def testBufferOutputStartTestAddSuccess(self):
        real_out = self._real_out
        real_err = self._real_err

        result = unittest2.TestResult()
        self.assertFalse(result.buffer)

        result.buffer = True

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

        result.startTest(self)

        self.assertIsNot(real_out, sys.stdout)
        self.assertIsNot(real_err, sys.stderr)
        self.assertIsInstance(sys.stdout, StringIO)
        self.assertIsInstance(sys.stderr, StringIO)
        self.assertIsNot(sys.stdout, sys.stderr)

        out_stream = sys.stdout
        err_stream = sys.stderr

        result._original_stdout = StringIO()
        result._original_stderr = StringIO()

        print('foo')
        sys.stderr.write('bar\n')

        self.assertEqual(out_stream.getvalue(), 'foo\n')
        self.assertEqual(err_stream.getvalue(), 'bar\n')

        self.assertEqual(result._original_stdout.getvalue(), '')
        self.assertEqual(result._original_stderr.getvalue(), '')

        result.addSuccess(self)
        result.stopTest(self)

        self.assertIs(sys.stdout, result._original_stdout)
        self.assertIs(sys.stderr, result._original_stderr)

        self.assertEqual(result._original_stdout.getvalue(), '')
        self.assertEqual(result._original_stderr.getvalue(), '')

        self.assertEqual(out_stream.getvalue(), '')
        self.assertEqual(err_stream.getvalue(), '')


    def getStartedResult(self):
        result = unittest2.TestResult()
        result.buffer = True
        result.startTest(self)
        return result

    def testBufferOutputAddErrorOrFailure(self):
        unittest2.result.traceback = MockTraceback
        self.addCleanup(restore_traceback)

        for message_attr, add_attr, include_error in [
            ('errors', 'addError', True),
            ('failures', 'addFailure', False),
            ('errors', 'addError', True),
            ('failures', 'addFailure', False)
        ]:
            result = self.getStartedResult()
            result._original_stderr = StringIO()
            result._original_stdout = StringIO()

            print('foo')
            if include_error:
                sys.stderr.write('bar\n')

            addFunction = getattr(result, add_attr)
            addFunction(self, (None, None, None))
            result.stopTest(self)

            result_list = getattr(result, message_attr)
            self.assertEqual(len(result_list), 1)

            test, message = result_list[0]
            expectedOutMessage = textwrap.dedent("""
                Stdout:
                foo
            """)
            expectedErrMessage = ''
            if include_error:
                expectedErrMessage = textwrap.dedent("""
                Stderr:
                bar
            """)

            expectedFullMessage = 'A traceback%s%s' % (expectedOutMessage, expectedErrMessage)

            self.assertIs(test, self)
            self.assertEqual(result._original_stdout.getvalue(), expectedOutMessage)
            self.assertEqual(result._original_stderr.getvalue(), expectedErrMessage)
            self.assertMultiLineEqual(message, expectedFullMessage)



if __name__ == '__main__':
    unittest2.main()
