CREATE OR REPLACE TEMPORARY TABLE {self._table_name} AS
(
    SELECT
            st.detection,
            ct.color,
            ct.varietal,
            chm.id,
            CONCAT_WS('_',st.samplecode, ct.wine) AS code_wine,
            cs.mins,
            {cs_col_list}
    FROM
    c_sample_tracker st
    INNER JOIN
        c_cellar_tracker ct ON st.ct_wine_name = ct.wine
    LEFT JOIN
        c_chemstation_metadata chm ON
            (
            chm.join_samplecode=st.samplecode
            )
    LEFT JOIN
        chromatogram_spectra cs ON (chm.id=cs.id)

    WHERE
        (
            (SELECT UNNEST($detection)) IS NULL
            OR st.detection IN (SELECT * FROM UNNEST($detection))
        )
    AND (
            (SELECT UNNEST($samplecode)) IS NULL
            OR st.samplecode IN (SELECT * FROM UNNEST($samplecode))
            )
    AND
    (
        (SELECT UNNEST($color)) IS NULL
            OR ct.color IN (SELECT * FROM UNNEST($color))
            )
        AND ((SELECT UNNEST($varietal)) IS NULL
            OR ct.varietal IN (SELECT * FROM UNNEST($varietal)))
        AND ((SELECT UNNEST($wine)) IS NULL
            OR ct.wine IN (SELECT * FROM UNNEST($wine)))
        AND ($min_start IS NULL OR cs.mins >= $min_start)
        AND ($min_end IS NULL OR cs.mins <= $min_end)
        AND ((SELECT UNNEST($exclude_samplecodes)) IS NULL
            OR st.samplecode NOT IN (SELECT * FROM UNNEST($exclude_samplecodes))
        )
        AND ((SELECT UNNEST($exclude_ids)) IS NULL
            OR chm.id NOT IN (SELECT * FROM UNNEST($exclude_ids))
        )
    )
    ORDER BY detection, color, varietal, code_wine, cs.id, mins