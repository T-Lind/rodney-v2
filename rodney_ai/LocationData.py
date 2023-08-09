import json


class LocationData:
    def __init__(self, filename=r"C:\Users\tenant\PycharmProjects\rodney-v2\rodney_ai\data\location_data.json"):
        self.filename = filename

    def _load_data(self):
        with open(self.filename, 'r') as file:
            return json.load(file)

    def get_gps_coordinate(self, abbr):
        data = self._load_data()
        for entry in data["locations"]:
            if entry["location_name"] == abbr:
                return [entry["gps_ew"], entry["gps_ns"]]
        return None  # Return None if the abbreviation wasn't found

    def get_gps_coordinate_json(self, location_entry_json):
        building_name = json.loads(location_entry_json)["building_name"]
        return self.get_gps_coordinate(building_name), building_name

    def get_file_text(self):
        with open(self.filename, 'r') as file:
            return file.read()
