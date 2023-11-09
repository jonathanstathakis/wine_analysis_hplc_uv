
# Inheritance

## OOP inheritance protection

uses underscores to indicate access privlage.

### Protected

single underscore, eg: _name, _method

For internal use only, should not be accessed outside class

### Private

start with double underscore, eg: __name, __method

This causes the interpreter to mangle the names, renaming the objects to include the class name: _ClassName_name

This causes them to be inaccessible form the subclass unless specifically using the mangled version.