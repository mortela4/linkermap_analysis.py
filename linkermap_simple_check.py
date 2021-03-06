"""
@file linkermap_simple_check.py
@brief Finds .text-entries, sorts thyem by size.
@note Assumes .MAP-file generated by GCC option '-Map=<mafile name>'.
"""


def correct_mapinfo_lines(lines: list, debug: bool = False) -> list:
    corrected_lines = list()
    keep = ''
    for line in lines:
        line = line.strip()
        if line.startswith('.text'):
            fields = line.split()
            if len(fields) == 1:
                keep = line
                continue
            else:
                corrected_lines.append(line)
        elif line.startswith('0x00000000'):
            line = keep + ' ' + line
            corrected_lines.append(line)
        else:
            pass
    #
    if debug:
        for corr_line in corrected_lines:
            print(corr_line)
    #
    return corrected_lines


def get_text_section_entries(mapfile: str, correct_lines: bool = False, debug: bool = False) -> list:
    text_section_lines = list()
    with open(mapfile, 'r') as fp:
        map_lines = fp.readlines()
    #
    if map_lines is None or len(map_lines) == 0:
        print("ERROR: got no lines in input (.MAP) file!")
        return None
    else:
        print("MAP-file size = %d lines ..." % len(map_lines))
    #
    if correct_lines:
        map_lines = correct_mapinfo_lines(map_lines)
    #
    for line in map_lines:
        line = line.strip()
        if line.startswith('.text'):
            text_section_lines.append(line)
            if debug:
                print("INFO: got .text-entry = '%s'" % line)
        else:
            if debug and len(line) != 0:
                print("Rejected line first field: %s" % line)
                pass
    #
    if debug:
        print("DEBUG: got %d .text-lines ..." % len(text_section_lines))
    return text_section_lines


def process_line(line: str, debug: bool = False) -> tuple:
    fields = line.split()
    #
    if len(fields) < 4:
        return None
    #
    func_name = fields[0].split('.')[-1]
    func_hex_size = fields[2]
    func_src_full = fields[3]
    #
    func_src = func_src_full.rstrip('.o') + '.c'
    try:
        func_size = int(func_hex_size, 16)
    except ValueError:
        if debug:
            print("ERROR: could not convert size field = '%s'!" % func_hex_size)
        return None
    #
    if func_size == 0:
        return None
    #
    return func_name, func_size, func_src


def sort_func_entries(entries: list, debug: bool = False) -> list:
    def get_size_field(item: tuple):
        return item[1]
    #
    map_info_list = list()
    for entry in entries:
        map_info = process_line(entry)
        if map_info is not None:
            if debug:
                print("INFO: mapinfo = '%s'" % str(map_info))
            map_info_list.append(map_info)
    #
    sorted_map_info = sorted(map_info_list, key=get_size_field, reverse=True)
    #
    return sorted_map_info


def pretty_print_mapinfo(entries: list):
    total_size = 0
    num_functions = len(entries)
    print("Function:\t\tSize:\t\tSource file:")
    print("====================================================")
    for map_info in entries:
        fname, fsize, fsrc = map_info
        print("%s\t\t\t\t\t\t\t\t\t%d\t\t\t%s" % (fname, fsize, fsrc))
        total_size += fsize
    #
    print("--------------------------------------------------------------------------------------------------")
    print("Total size: %d bytes" % total_size)
    print("Total # of functions: %d" % num_functions)


def dump_mapinfo_to_csv(entries: list, csv_name: str):
    csv_entries = list()
    header = "Function Name,Function Size,Source file\n"
    csv_entries.append(header)
    #
    for map_info in entries:
        fname, fsize, fsrc = map_info
        mapinfo_line = fname + ',' + str(fsize) + ',' + fsrc + '\n'
        csv_entries.append(mapinfo_line)
    #
    with open(csv_name, 'w') as fp:
        map_lines = fp.writelines(csv_entries)
    #
    print("\n%d entries written to CSV-file '%s' ..." % (len(entries), csv_name))


# *************************** MAIN *********************************
if __name__ == "__main__":
    mapinfo_lines = get_text_section_entries("test.map", correct_lines=True)
    textinfo = sort_func_entries(mapinfo_lines)
    pretty_print_mapinfo(textinfo)
    dump_mapinfo_to_csv(textinfo, "test.csv")





