from parsing_service.implementation.parser_factory import parse_file, parse_file_to_json
import json
import pandas as pd
import os

file = "base.pdf"
path = "/Users/annamarika/PycharmProjects/text-extractor/samples"
parsed_file = parse_file_to_json(path, file, "pdf")
print(parsed_file)

if isinstance(parsed_file, pd.Series):
    dfs = parsed_file.tolist()
    for i, df in enumerate(dfs):
        df.to_csv(f"/Users/annamarika/tabella_{i}.csv")

elif parsed_file.endswith('.json'):
    with open(parsed_file, 'r') as json_file:
        json_data = json.load(json_file)
    filename = os.path.basename(parsed_file)
    with open(f"/Users/annamarika/Desktop/{filename}", 'w') as file:
        json.dump(json_data, file, indent=2)
else:
    with open("/Users/annamarika/Desktop/prova.txt", 'w') as file:
        for chunk in parsed_file:
            file.write(str(chunk) + "\n")
