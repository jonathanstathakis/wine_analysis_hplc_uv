def rename_wine_deg_wines(new_id_series: pd.Series):
    """
    Use regex to find the wines exp_id then replace with the sample_tracker id.add()
    pattern = .[01]..
    """
    # Define the regex pattern and replacement mapping
    pattern = r"^[nea](01|02|03)"
    replacement = {"01": "103", "02": "104", "03": "105"}

    # Replace the strings in the 'new_id' column
    # using the regex pattern and replacement mapping
    new_id_series = new_id_series.replace(
        pattern, lambda x: replacement[x.group(1)], regex=True
    )

    return new_id_series
