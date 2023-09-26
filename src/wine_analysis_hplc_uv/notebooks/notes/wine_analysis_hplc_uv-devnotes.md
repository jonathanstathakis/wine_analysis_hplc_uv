## Finalizing Library Pipe

[logbook backlink]

2023-05-15 15:19:38

raw chemstation pipe works.

raw sampletracker pipe works.

raw cellartracker pipe works.

2023-05-15 16:11:33

Use 

```bash
duckdb $WINE_AUTH_DB_PATH -c "show tables;"  
```

For example to quickly query the current db. Useful for checking changes made by python scripts.