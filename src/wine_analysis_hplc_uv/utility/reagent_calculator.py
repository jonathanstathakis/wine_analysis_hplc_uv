import pandas as pd


def reagent_calculator(desired_vol: float):
    """
    Desired volume is the final volume after combining the reagents i.e. 3 x reagent volume
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

    cop_chlor["solvent"] = "H2O"
    neocup["solvent"] = "MeOH"
    amac["solvent"] = "H2O"

    # mol/L
    cop_chlor["final_conc"] = 0.01
    neocup["final_conc"] = 0.0075
    amac["final_conc"] = 1
    """
    calculate volume of each required sample
    """

    df = pd.DataFrame([cop_chlor, neocup, amac], index=["cop_chlor", "neocup", "amac"])

    df["required_vol"] = desired_vol / 3

    df["moles"] = df["final_conc"] * df["required_vol"]

    df["mass (g)"] = df["molar_mass"] * df["moles"]

    print(df.to_markdown())


def main():
    reagent_calculator(desired_vol=3)


if __name__ == "__main__":
    main()
