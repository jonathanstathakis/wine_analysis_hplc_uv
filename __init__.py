.
├── __init__.py
├── cellartracker
│   ├── __init__.py
│   ├── cellartracker_cleaner.py
│   └── init_raw_cellartracker_table.py
├── chemstation
│   ├── __init__.py
│   ├── chemstation_metadata_table_cleaner.py
│   ├── chemstation_methods.py
│   ├── chemstation_to_db_methods.py
│   └── init_chemstation_data_metadata.py
├── core
│   ├── __init__.py
│   ├── adapt_super_pipe_to_db.py
│   └── build_library.py
├── core.py
├── credientals_tokens
│   ├── credentials_sheets.json
│   ├── token_sheets.json
│   └── wine_auth_db.db
├── data
│   └── 2023-02-09_14-30-37_Z3_uv-data.csv
├── db_methods
│   ├── __init__.py
│   └── db_methods.py
├── devtools
│   ├── __init__.py
│   └── function_timer.py
├── df_methods
│   ├── __init__.py
│   ├── df_cleaning_methods.py
│   └── df_methods.py
├── etc
│   └── jupyter
│       ├── jupyter_notebook_config.d
│       │   └── panel-client-jupyter.json
│       ├── jupyter_server_config.d
│       │   └── panel-client-jupyter.json
│       └── nbconfig
│           └── notebook.d
│               └── widgetsnbextension.json
├── example_data
│   └── 2023-02-23_LOR-RISTRETTO.D
│       ├── ACQRES.REG
│       ├── CSlbk.ini
│       ├── DA.M
│       │   ├── DAMETHOD.REG
│       │   ├── INFO.MTH
│       │   ├── RECALIB.MTH
│       │   └── rpthead.txt
│       ├── DAD1.UV
│       ├── DAD1A.ch
│       ├── DAD1B.ch
│       ├── DAD1C.ch
│       ├── DAD1D.ch
│       ├── DAD1E.ch
│       ├── DAD1F.ch
│       ├── LCDIAG.REG
│       ├── RUN.LOG
│       ├── SAMPLE.XML
│       ├── SAMPLE.XML.bak
│       ├── SINGLE.B
│       ├── acq.macaml
│       ├── acq.txt
│       ├── da.macaml
│       └── sample.acaml
├── google_sheets_api
│   ├── __init__.py
│   └── google_sheets_api.py
├── include
│   └── python3.11
├── peak_alignment_pipe_pickle_jar
├── plot_methods
│   ├── __init__.py
│   ├── plotly_plot_methods.py
│   └── sns_plot_methods.py
├── prototypes
│   ├── __init__.py
│   ├── chrom_quality_analyser.py
│   └── observing_spectra_shape_variation.py
├── pyvenv.cfg
├── sampletracker
│   ├── __init__.py
│   ├── init_raw_sample_tracker_table.py
│   ├── sample_tracker_cleaner.py
│   └── sample_tracker_methods.py
├── scripts
│   ├── __init__.py
│   ├── acaml_read.py
│   ├── core_scripts
│   │   ├── __init__.py
│   │   ├── data_interface.py
│   │   ├── data_manipulators.py
│   │   ├── hplc_dad_plots.py
│   │   ├── signal_data_treatment_methods.py
│   │   └── wine_auth_db.db
│   ├── old_scripts
│   │   ├── __init__.py
│   │   ├── combo_dif.py
│   │   ├── dir_contents_dict_builder.py
│   │   ├── dir_ext_set_getter.py
│   │   ├── example_getopt.py
│   │   ├── playing_with_argpase.py
│   │   └── uv_to_csv.py
│   ├── reagent_calculator.py
│   ├── remove_empty_sequences.py
│   └── setup.py
├── signal_processing
│   ├── __init__.py
│   ├── peak_alignment
│   │   ├── __init__.py
│   │   ├── peak_alignment_pipe.py
│   │   └── peak_alignment_spectrum_chromatograms.py
│   ├── signal_alignment_methods.py
│   └── signal_data_treatment_methods.py
├── streamlit_methods
│   ├── __init__.py
│   └── streamlit_spectra_display.py
├── test_dir_empty
├── tests
│   ├── test_spectra_df.py
│   └── testing_reading_db.py
├── wine_analysis_hplc_uv.code-workspace
└── wine_deg_study
    ├── 2023-04-11_sequence_planner.ipynb
    ├── 2023-04-11_wine_deg_sample_tracker_creation.ipynb
    ├── experiment_planner.py
    └── time_step_schedule.py

33 directories, 95 files
