
-- unpivot and cast wavelength to int by removing the unit suffix.
-- expected to take ~1 minute 15 seonds on the full dataset (175 samples)
create table pbl.chromatogram_spectra_long AS
with
	cs as (select * from main.chromatogram_spectra),

    -- add a time ordered unique row index, sample specific
	number_cs_rows AS (SELECT
        row_number() OVER (PARTITION BY cs.id ORDER BY cs.mins)-1 AS idx,
        * FROM
        cs),

    -- unpivot from wide to long
    melt_cs as (
        unpivot number_cs_rows
         on * exclude (id, mins, idx)
         INTO name wavelength value absorbance),

    -- alter wavelength column - remove the unit suffix and cast int
   split_wavelength as (
        select
        idx,
        id,
        mins,
        cast(split_part(wavelength, '_',2) as int) as wavelength,
        absorbance
        from
            melt_cs)
select * from split_wavelength;
