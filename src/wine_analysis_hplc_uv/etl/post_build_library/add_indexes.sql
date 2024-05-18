-- add index on id in both sample metadata and chromatogram_spectra

-- metadata

create index metadata_id_idx on c_chemstation_metadata (id);

-- chromato-spectra

create index cs_id_idx on chromatogram_spectra (id);
