CREATE OR REPLACE VIEW wine_data AS
SELECT st.detection,
    st.samplecode,
    ct.wine,
    ct.color,
    ct.varietal,
    chm.id,
    cs.mins,
    cs.wavelength,
    cs.value
FROM c_sample_tracker st
    INNER JOIN c_cellar_tracker ct ON st.ct_wine_name = ct.wine
    LEFT JOIN c_chemstation_metadata chm ON (
        chm.join_samplecode = st.samplecode
    )
    LEFT JOIN chromatogram_spectra cs ON (chm.id = cs.id)
-- WHERE (
--         (
--             SELECT UNNEST($detection)
--         ) IS NULL
--         OR st.detection IN (
--             SELECT *
--             FROM UNNEST($detection)
--         )
--     )
--     AND (
--         (
--             SELECT UNNEST($samplecode)
--         ) IS NULL
--         OR st.samplecode IN (
--             SELECT *
--             FROM UNNEST($samplecode)
--         )
--     )
--     AND st.samplecode NOT IN ('72', '98')
--     AND (
--         (
--             SELECT UNNEST($color)
--         ) IS NULL
--         OR ct.color IN (
--             SELECT *
--             FROM UNNEST($color)
--         )
--     )
--     AND (
--         (
--             SELECT UNNEST($varietal)
--         ) IS NULL
--         OR ct.varietal IN (
--             SELECT *
--             FROM UNNEST($varietal)
--         )
--     )
--     AND (
--         (
--             SELECT UNNEST($wine)
--         ) IS NULL
--         OR ct.wine IN (
--             SELECT *
--             FROM UNNEST($wine)
--         )
--     )
    -- AND (
    --     (
    --         SELECT UNNEST($wavelength)
    --     ) IS NULL
    --     OR cs.wavelength IN (
    --         SELECT *
    --         FROM UNNEST($wavelength)
    --     )
    -- )
--     AND (
--         $min_start IS NULL
--         OR cs.mins >= $min_start
--     )
--     AND (
--         $min_end IS NULL
--         OR cs.mins <= $min_end
--     )