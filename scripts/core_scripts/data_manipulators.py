import pandas as pd

def df_windower(wide_df = pd.DataFrame, dimension = str, min_val = int, max_val = int):
    
    try:
    
        melt_d = wide_df.melt(id_vars = 'mins', value_name = 'mAU', var_name = 'nm')
    
    except Exception as e:
        print(f"{e}")
              
    try:
    
        melt_d = melt_d[(melt_d[f"{dimension}"] > min_val) & (melt_d[f"{dimension}"] < max_val)]

    except Exception as e:
        print(f"{e}")

    try:
              
        pivot_d = melt_d.pivot(columns = ['nm'], values = 'mAU', index = 'mins')
    
        pivot_d = pivot_d.reset_index()
    
    except Exception as e:
        print(f"{e}")
    
    return pivot_d