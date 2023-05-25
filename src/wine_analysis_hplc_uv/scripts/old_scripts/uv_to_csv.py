import rainbow as rb


def uv_to_csv(in_path=str, out_path=str):
    print("in_path is: {}".format(in_path))

    uv_data = rb.agilent.chemstation.parse_uv(in_path)

    print("shape of the uv data is: {}".format(uv_data.data.shape))

    # Convert the data to csv

    try:
        uv_data.export_csv(out_path)
        print("csv of UV data exported to: {}".format(out_path))

    except Exception as e:
        print("export error {}, try again".format(e))


def main():
    # uv_to_csv(in_path = input("inpath:"), out_path = input("outpath:"))

    uv_to_csv(in_path=input("inpath: "), out_path=input("outpath: "))


main()

# /Users/jonathan/0_jono_data/2023-02-14_0052_TESTING_COLUMN_FOR_SAMPLE_DEG.D/DAD1.UV

# /Users/jonathan/0_jono_data/2023-02-14_0052_TESTING_COLUMN_FOR_SAMPLE_DEG.D/DAD1.csv
