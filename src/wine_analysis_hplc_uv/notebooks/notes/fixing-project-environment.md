### Fixing Poetry setup

2023-06-16 01:54:14

Yet again it looks as though there is a problem with my project setup. I need to take this seriously, and figure out how to get this to work. To figure out the problem:

TODO:

- [x] setup test project
- [x] setup second test project
- [x] install test project into second test project.
- [x] compare setup of first project with wine_analysis_hplc_uv

Looks like I fixed it. Problem was that I've moved the package files to '~/src/wine_analysis_hplc_uv' but pyproject.toml had `packages = [{include = "wine_analysis_hplc_uv"}]` which it couldnt find. adding "src" to the path fixed it:  `packages = [{include = "src/wine_analysis_hplc_uv"}`. Have commited a corrected update.

[[python_poetry_setup]]

2023-06-16 13:47:01

Not quite fixed. While the packages are poetry installable, they arn't importable. This includes wine_analysis_hplc_uv, mydevtools, and a test_project generated with `poetry new`. The only thing they have in common is that I'm adding them as 'editable'.

I have reverted changes in both mydevtools and wine_analysis_hplc_uv, but to no avail. time to setup the test environments again.

TODO:
- [x] setup test environment: test_project_1, test_project_2.
- [x] try to import test_project_2 into test_project_1

To understand the functionality, ill test importing after every 'stage':

in test_project_1:
1. `poetry add test_project_2` - import doesnt work
2. `poetry install` - import doesnt work

Nothing worked.

I've also tried a git repo install of test_project_2, doesnt work either. I think I now need to learn how [[python_import|imports]] work. hopefully once i understand where everything is looking, the root cause will become apparent.

2023-06-17 23:37:36

Got it. Bloody VSCode. For some reason its stopped automatically detecting the poetry virtualenv. I diagnosed this by checking `sys.path` in the CLI REPL, where I could see the installed package path in the list. To fix this I used `poetry show -v` to get the virtualenv interpreter path, then entered that into the interpreter prompt.

2023-06-18 17:29:29

But then another thing broke. For some inexplixable reason, wine_analysis_hplc_uv was no longer importable within itself, even though it was in `sys.path`. Removing:

```
packages = [{include = "src/wine_analysis_hplc_uv"}]
```

fixed it. Dont know what that's about, but it looks like the environment is happy again.

2023-06-21 09:48:28 Amend: Yesturday I found that a local .venv and the defualt poetry .venv were clashing, as I had not set up poetry to use a local venv. Deleting the local .venv (an artifact from the pre-poetry configuration) seems to have fixed import issues for good. Need to make sure `poetry shell` is run though, VSCode does not seem to be automatically activating the venv.