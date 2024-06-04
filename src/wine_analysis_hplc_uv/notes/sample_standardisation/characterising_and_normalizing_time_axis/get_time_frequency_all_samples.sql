-- round to 10 decimal places to account for floating point error
CREATE OR REPLACE TEMP MACRO round_(a) AS round(a, 10);

-- A macro to produce an observation of the time difference of every sample in the dataset
CREATE OR REPLACE TEMP MACRO observe_time_offset() AS TABLE
(
    SELECT
        -- cs.id,
        dense_rank() OVER (ORDER BY cs.id) as sample_num,
        row_number() OVER (PARTITION BY cs.id ORDER BY cs.mins)-1 AS idx,
        sm.samplecode,
        sm.wine,
        round_(cs.mins) as mins,
        round_(mins * 60) AS seconds,
        lag(seconds, 1, NULL) OVER (PARTITION BY cs.id ORDER BY cs.mins) as shift_seconds,
        round_(seconds - shift_seconds) AS diff_seconds,
    FROM
        (
    SELECT *
    FROM
        chromatogram_spectra_long
    WHERE
        wavelength = 200
) as cs
    INNER JOIN
        (
    SELECT *
    FROM
        sample_metadata
) as sm
        ON
            cs.id = sm.id
)
ORDER BY sample_num ASC, seconds ASC;

SELECT * FROM observe_time_offset();

-- -- calculate the mode of each samples difference
-- CREATE OR REPLACE TEMP TABLE wine_seconds_agg
-- AS (
--     SELECT
--         first(samplecode) as samplecode,
--         first(wine) as wine,
--         1/ mode(diff_seconds) as mode_diff_hertz,
--     FROM
--         wine_seconds
--     GROUP BY wine
-- );

-- -- calculate the mode of modes
-- CREATE OR REPLACE TEMP TABLE average_mode_over_samples
-- AS
--     (
--         SELECT
--             mode(mode_diff_hertz) as dataset_mode_hertz
--         FROM
--             wine_hertz_agg
--     );

-- -- count unique values for sample mode

-- CREATE OR REPLACE TEMP TABLE mode_counts
-- AS (
--     SELECT
--         -- DISTINCT mode_diff_hertz as mode_unique,
--         COUNT(mode_diff_hertz)
--     FROM
--         wine_hertz_agg
--     GROUP BY mode_diff_hertz
-- );