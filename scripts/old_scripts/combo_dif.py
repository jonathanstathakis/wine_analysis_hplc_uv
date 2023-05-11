difference_list = []


def combo_diff_printer(combo):
    for idx, pair in enumerate(combo):
        if ".D" in pair[0] and ".D" in pair[1]:
            print("###########################################\n")

            difference = ext_set_dict[pair[0]].symmetric_difference(
                ext_set_dict[pair[1]]
            )

            print("#", idx, pair, "\n")

            if not difference:
                print("no differences in subdirectories\n")
                continue

            else:
                print(difference, "\n")

                difference_list.append("item {} had a difference".format(idx))

                for item in difference:
                    if item in ext_set_dict[pair[0]]:
                        print(item, "belongs to", pair[0])
                    if item in ext_set_dict[pair[1]]:
                        print(item, "belongs to", pair[1])

                    print("\n")


print(difference_list)
if not difference_list:
    "no differences detected"
