import traceback


def test_report(tests: list):
    def try_pass_fail(func, *args, _count=[0], **kwargs):
        _count[0] += 1

        test_dict = dict(
            func_name=func.__name__, result=0, exception="", value="", tb=""
        )

        print(f"test {_count[0]}: {test_dict['func_name']}..", end=" ")

        bool_args = bool(args)
        try:
            if bool_args:
                test_dict["value"] = func(*args, **kwargs)
            else:
                test_dict["value"] = func()
        except Exception as e:
            test_dict["exception"] = repr(e)
            test_dict["tb"] = traceback.format_exc()

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
    print("")
    for test in test_dicts:
        if test["result"] == 0:
            print(
                f"Test '{test['func_name']}' failed with exception: {test['exception']}"
            )
            print("")
            print(test["tb"])

    return None
