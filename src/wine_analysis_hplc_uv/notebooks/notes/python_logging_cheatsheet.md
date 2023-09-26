# Python Logging

2023-06-08 14:10:57

Testing the ChemstationProcessor necessitated the introduction of [logging](https://docs.python.org/3/howto/logging.html) to control the verbosity of the package. This allows me to set levels of verbosity depending on the use case. It will now be in every package I write with the following pattern:

For a package named example_package, In example_package root __init__.py:

```python
import logging

logger = logging.getLogger(__name__)
```

and in every module of that example_package:

```python
from example_package import logger
```

And instead of `print()`, use logger.LEVEL() where level can be info, debug, warning, etc (refer to docs) i.e.

```python
logger.info("this is information everyone should know")
logger.debug("this is information that should only be seen during debugging")
```

In packages wanting to control the logging behavior, use, for example:

```python
import logging

logging.basicConfig(level=logging.INFO)
example_package_logger = logging.getLogger("example_package.module")
example_package_logger.setLevel(logging.INFO)
test_logger = logging.getLogger(__name__)
```

Will allow you to control the verbosity of the test module log and individual package logs. Note that "module" in this case is for a slipecific module of the package, i.e. the `__name__` variable. Can specify for anything. Also, `.setlevel` is where you control the verbosity, again, check the docs.