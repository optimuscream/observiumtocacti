#!/usr/bin/env python
# Convert rrd data from observium to cacti rrd
# Remove all other DS other than traffic_in and traffic_out
#

import sys
import xml.etree.ElementTree as ET

def filter_and_modify_rrd_dump(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Define allowed DS names and their replacements
    name_map = {
        "inoctets": "traffic_in",
        "outoctets": "traffic_out"
    }
    
    allowed_names = list(name_map.keys())  # Maintain order for mapping

    # Step 1: Process <ds> elements in <rrd>
    ds_parent = root  # <ds> elements are directly under <rrd>
    ds_elements = ds_parent.findall("ds")
    kept_ds_count = 0  # Counter for valid DS elements

    for ds in ds_elements:
        name_element = ds.find("name")
        type_element = ds.find("type")

        if name_element is not None:
            original_name = name_element.text.strip().lower()
            if original_name in name_map:
                # Rename DS name
                name_element.text = name_map[original_name]
                # Change type to COUNTER
                if type_element is not None:
                    type_element.text = "COUNTER"
                kept_ds_count += 1
            else:
                ds_parent.remove(ds)  # Remove unwanted DS

    # Step 2: Process <cdp_prep> section
    for cdp_prep in root.findall(".//cdp_prep"):
        ds_cdp_elements = cdp_prep.findall("ds")

        # Keep only first `kept_ds_count` <ds> elements in <cdp_prep>
        for ds in ds_cdp_elements[kept_ds_count:]:
            cdp_prep.remove(ds)

    # Step 3: Process <database> section
    for database in root.findall(".//database"):
        for row in database.findall("row"):
            v_elements = row.findall("v")

            # Keep only the first `kept_ds_count` <v> elements in each row
            for v in v_elements[kept_ds_count:]:
                row.remove(v)

    # Step 4: Write back the modified XML file
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print("Filtered RRD XML written to {}".format(output_file))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.xml output.xml")
        sys.exit(1)

    filter_and_modify_rrd_dump(sys.argv[1], sys.argv[2])
