separator = ","  # Separator used for datalines


# NamedTuple formatted to string e.g. "item,item,item\n"
def format_named_tuple(nt):
    value_list = list(nt._asdict().values())
    string_list = [str(val) for val in value_list]
    return separator.join(string_list) + "\n"
