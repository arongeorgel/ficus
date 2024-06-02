import datetime
import json

class DataHandler:
    def __init__(self, data):
        self.data = data

    def save_to_json(self, file_path):
        with open(file_path, 'w') as file:
            json_data = [{**item, 'time': item['time'].isoformat()} for item in self.data]
            json.dump(json_data, file, indent=4)

# Example usage
data = [
    {"event": "event1", "time": datetime.datetime(2024, 5, 31, 12, 52, 8, tzinfo=datetime.timezone.utc)},
    {"event": "event2", "time": datetime.datetime(2024, 6, 1, 14, 30, 0, tzinfo=datetime.timezone.utc)}
]

handler = DataHandler(data)
handler.save_to_json('data.json')
