"""
source:

https://opensourceoptions.com/blog/how-to-pass-arguments-to-a-python-script-from-the-command-line/#:~:text=In%20Python%2C%20arguments%20are%20passed,used%20to%20parse%20named%20arguments.
"""

import sys
import getopt


def myfunc(argv):
    arg_input = ""
    arg_output = ""
    arg_user = ""
    arg_help = "{0} -i <input> -u <user> -o <output>".format(argv[0])

    try:
        opts, args = getopt.getopt(
            argv[1:], "hi:u:o:", ["help", "input=", "user=", "output="]
        )
    except Exception as e:
        e.add_note(arg_help)
        raise e

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-i", "--input"):
            arg_input = arg
        elif opt in ("-u", "--user"):
            arg_user = arg
        elif opt in ("-o", "--output"):
            arg_output = arg

    print("input:", arg_input)
    print("user:", arg_user)
    print("output:", arg_output)


if __name__ == "__main__":
    myfunc(sys.argv)
