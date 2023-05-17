"""
A file containing misc ux methods.
"""


from typing import Any, Callable

def ask_user_and_execute(prompt: str, func: Callable[..., Any], *args: Any, **kwargs: Any):
    """
    For yes/no questions, currently used to break the build_library pipe up into chunks for bug testing or isolation of function within the program.
    Provide a prompt, a function name and arguments, and let it do the rest.- 
    """
    bad_input = True
    while bad_input:
        user_input = input(f"{prompt} (y/n): ").strip().lower()
        print("")
        if user_input == 'y':
            bad_input = False
            result = func(*args, **kwargs)
        elif user_input == 'n':
            bad_input = False
            result = None
            break
        else:
            print("Bad input, try again..\n")
            continue
    return result