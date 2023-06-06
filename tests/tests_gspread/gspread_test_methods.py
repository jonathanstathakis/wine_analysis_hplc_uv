"""
Methods for testing gspread.

Contains:

try_pass_fail: a soon-to-be wrapper that takes a function and args, tries to execute it, and reports the status. returns a dict containig:
- func_name: str = "", name of the passed function
- result: bool = 0, 0 for fail, set to 1 for test pass.
- exception: str = "", if fail, error message is stored as a string.
- value: str = "", to store the output of the tested function

test_report:
Takes a list of tuples of `(function object, args)` and runs try_pass_fail on each of them, assembling a list of dicts of the results of the tests, then reports them.

Note: no need to import try_p
"""

import os


def get_test_key():
    return os.environ.get("TEST_SAMPLETRACKER_KEY")


def test_report(tests: list):
    def try_pass_fail(func, *args, _count=[0], **kwargs):
        _count[0] += 1

        test_dict = dict(func_name=func.__name__, result=0, exception="", value="")

        print(f"test {_count[0]}: {test_dict['func_name']}..", end=" ")

        bool_args = bool(args)
        try:
            if bool_args:
                test_dict["value"] = func(*args, **kwargs)
            else:
                test_dict["value"] = func()
        except Exception as e:
            test_dict["exception"] = repr(e)
        else:
            test_dict["result"] = 1

        if test_dict["result"]:
            print(f"passed")
        elif not test_dict["result"]:
            print("failed")

        return test_dict

    test_dicts = [try_pass_fail(func, *args) for func, *args in tests]

    test_pass_count = sum(test_dict["result"] for test_dict in test_dicts)
    test_fail_count = len(tests) - test_pass_count

    print("")
    print(f"tests passed: {test_pass_count}")
    print(f"tests failed: {test_fail_count}")
    print("")

    print("tests passed:")
    for test in test_dicts:
        if test["result"] == 1:
            print(test["func_name"])

    print("")
    print("tests failed:")
    for test in test_dicts:
        if test["result"] == 0:
            print(
                f"Test '{test['func_name']}' failed with exception: {test['exception']}"
            )

    return None
