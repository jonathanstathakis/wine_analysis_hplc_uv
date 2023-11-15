SELECT
    *
FROM
chromatogram_spectra
WHERE
    mins>20
AND
    mins<21
LIMIT 10