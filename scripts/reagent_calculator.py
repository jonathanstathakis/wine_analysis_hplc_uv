import pandas as pd


def reagent_calculator(desired_vol : float):
    """
    Desired volume is the final volume after combining the reagents i.e. 3 x reagent volume
    """

    """
    For say 100mL target
    c = m/V
    m = c * V
    """
    
    cop_chlor = {}
    neocup = {}
    amac = {}

    cop_chlor["molar_mass"] = 170.48
    neocup["molar_mass"] = 208.26
    amac["molar_mass"] = 77.08
    
    # mol/L
    cop_chlor["final_conc"] = 0.01
    neocup["final_conc"] = 0.075
    amac["final_conc"] = 1
    """
    calculate volume of each required sample
    """

    df = pd.DataFrame([cop_chlor, neocup, amac], index = ['cop_chlor', 'neocup','amac'])
    
    df['required_vol'] = desired_vol/3

    df['moles'] = df['final_conc'] * df['required_vol']

    df['mass (mg)'] = df['molar_mass'] * df['moles']

    print(df)

def main():
    reagent_calculator(desired_vol = 300)

if __name__ == "__main__":
    main()