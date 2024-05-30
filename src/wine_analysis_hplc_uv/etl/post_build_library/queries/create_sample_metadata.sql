create table pbl.sample_metadata as
with sm as (
    select
        st.detection,
        chm.acq_date,
        ct.wine,
        ct.color,
        ct.varietal,
        st.samplecode,
        chm.id,
        dense_rank() over (order by chm.acq_date) as sample_num
    from
        c_chemstation_metadata as chm
    left join
        c_sample_tracker as st
        on chm.join_samplecode = st.samplecode
    left join
        c_cellar_tracker as ct
        on st.ct_wine_name = ct.wine
    order by sample_num
)
select * from sm;
