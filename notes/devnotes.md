# Development Notes

Notes on project development go here.

2023-09-07 13:18:55 - Have added [nbstripout](https://github.com/kynan/nbstripout) as a pre-commit hook to ensure that notebooks are never commited with output. This hook will check if there is output, and clear it if so, simply requiring you to add the change before commiting again.

## Database IO

### Designing a Query API

2024-05-03 15:24:29

I need specific logic for each table and column type. this is divided into: whether the input is an iterable or a scalar.

what are the modes of operation? If no argument is submitted, dont add a WHERE to the query. if its an iterable, use IN, and if its a scalar, use '='.

further logic is needed for the wavelength and mins columns, where ease of use requires the input of ranges.

I could continue to subset the relation as it is lazily evaluated, but in the interest of reducing the amount of python logic, we will instead use query string generation.

iterate through the options, and if present in the dict, initiate further logic

UPDATE: this approach has been shelved, instead will assemble a full sampleset metadata table and filter on that, not large enough to need further optimization.

2024-05-05 17:39:43

Have decided to establish an ETL orchastration class. It will be superficially modelled after the sklearn Pipeline, in that it will take a list of iniitalised transformation classes and execute them uing a method call "execute_pipeline". The Pipeline will expect the Transform classes to possess a 'run' method which will be the top level class. On calling the Pipeline "execute_pipeline", the Pipeline object will iterate through the Transformer list and call their "run" methods. Each Transformer will also be responsible for providing a cleanup method to undo the action of 'run', in the event of an error. The pipeline will execute each Transformer.run in the order they are provided, and if an error occurs, execute Transformer.cleanup in reverse order.

2024-05-06 08:39:55

The pipeline and two tranformers: BuildSampleMetaData, CSWideToLong are completed and tested.

Now to write a query class. Take a mapping of selection values and return a data table. Have an option to retrieve the chromatogram data or not.

This query class will be found in "queries.py".

# Designing a Query Generator

## of course we could simply the whole thing by simply injecting strings from the filter dict...
## this indicates that we actually need two things - a query generator and a top level user API.
## the query generator will take a dict with keys pointing to the relevent field, iterate through it and generate the query string.

# Simplifying the problem

the problem I am actually trying to solve is sthe slow time joining the metadata with the chromatogram images. We could reduce the complexity by creating the full metadata table as another table then simply filtering on that. Then we dont need to add the filter to the sub tables. Call it 'all_samples_metadata'.

# Useful Regex

2024-05-07 20:01:43

VSCodes 'Find All References' function is untrustworthy. To find imports in the package, use this template "<start of import>^([^\s]+ ).*( .*)<end of import>". See [stack overflow](https://stackoverflow.com/a/76129640/18650135)

