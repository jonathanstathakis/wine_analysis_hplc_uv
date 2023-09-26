---
creation-date: 2023-06-15-14-32-36
mod-date:
tag: 2023, sql
alias:
---
<!--begin_file -->

<!--header -->

# SQL Pattern Matching

## Related

[[sql]]
[[2023-06-15]]

<!-- contents -->

```SQL
SELECT
  column_list
From
  table_name
WHERE
  column_1 LIKE pattern;
```

wildcard matching is achieved with '%' (greedy) or '_' (not greedy).

Note, the pattern needs to be wrapped in quotes to tell SQL its a string. i.e.:

```bash
 duckdb $DB_DIR_PATH -c "SELECT * FROM tbl where name like '%patt%';"
```

To be case insensitive, use `ILIKE`

## References

<!--end_file -->