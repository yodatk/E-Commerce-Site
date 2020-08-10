import csv
import os

import os


class AcceptanceTestDataObject:
    # init method or constructor
    def __init__(self, component):
        self.test_case_inputs = self.import_from_csv(component)
        self.set_up_shopping_data = self.import_setup_from_csv()


    def correct_type(self, entry):
        try:
            return int(entry)
        except ValueError:
            try:
                return float(entry)
            except ValueError:
                lowered = entry
                lowered = lowered.lower()
                if lowered == "true":
                    return True
                elif lowered == "false":
                    return False
                else:
                    return entry

    def import_from_csv(self, component):
        data_dict = {}
        key = ""
        component_corrected = component[len("test_"):]
        dirname, _ = os.path.split(os.path.abspath(__file__))
        path = dirname+"\\"+component_corrected+'.csv'

        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if not self.is_comment(row):
                    if row[0] == '': #then there is data in this row
                        spliced = list(map(lambda x: self.correct_type(x), row[1:]))
                        expected = spliced.pop()
                        params = tuple(spliced)
                        data_dict[key].append((key, params, expected))

                    else:       #then its an AT number
                        key = row[0]
                        data_dict[key] = []
        return data_dict

    def import_setup_from_csv(self):
        setup_dict = {}
        is_users = is_stores = False
        user_header = store_header = inventory_header = []
        dirname, _ = os.path.split(os.path.abspath(__file__))
        path = dirname+"\\setup.csv"
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[0] == '':  # then there is data in this row
                    data_type_converted = list(map(lambda x: self.correct_type(x), row[1:]))
                    if is_users:
                        header = user_header
                    elif is_stores:
                        header = store_header
                    else:
                        header = inventory_header

                    entry_dict = {}
                    for field, data in zip(header[1:], data_type_converted):
                        entry_dict[field] = data
                    section_name = header[0]
                    setup_dict[section_name].append(entry_dict)
                else:  # then its a section header
                    key = row[0]
                    if key == "Users":
                        is_users = True
                        is_stores = False
                        user_header = row
                    elif key == "Stores":
                        is_stores = True
                        is_users = False
                        store_header = row
                    elif key == "Inventory":
                        is_users = is_stores = False
                        inventory_header = row
                    else:
                        raise Exception("Incompatible key : {key}".format(key=key))

                    setup_dict[key] = []
        setup_dict["Purchases"] = []
        return setup_dict


    def get_case_data(self, test_id):
        return self.test_case_inputs[test_id]


    def correct_type(self, entry):
        try:
            return int(entry)
        except ValueError:
            try:
                return float(entry)
            except ValueError:
                lowered = entry
                lowered = lowered.lower()
                if lowered == "true" or lowered == "success":
                    return True
                elif lowered == "false" or lowered == "failure":
                    return False
                else:
                    return entry

    def is_comment(self, row):
        return row[0] == "#"


