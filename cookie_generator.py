import json

with open('cookie.json', 'r') as file:
    data = json.load(file)

result = {}
for item in data:
    name = item.get("name")
    value = item.get("value")
    if name and value:
        result[name] = value

with open('output_file.json', 'w') as file:
    json.dump(result, file, indent=4)
