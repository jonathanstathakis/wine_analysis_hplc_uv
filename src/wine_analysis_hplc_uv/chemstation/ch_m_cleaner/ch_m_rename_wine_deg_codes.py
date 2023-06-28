def rename_wine_deg_wines(join_samplecode_series: pd.Series):
    """
    Use regex to find the wines exp_id then replace with the sample_tracker id.add()
    pattern = .[01]..
    """
    # Define the regex pattern and replacement mapping
    pattern = r"^[nea](01|02|03)"
    replacement = {"01": "103", "02": "104", "03": "105"}

    # Replace the strings in the 'join_samplecode' column
    # using the regex pattern and replacement mapping
    join_samplecode_series = join_samplecode_series.replace(
        pattern, lambda x: replacement[x.group(1)], regex=True
    )

    return join_samplecode_series
