from parsing_service.implementation.parser_factory import parse_file
import json
import pandas as pd

parsed_file = parse_file("samples/file1.pdf", "pdf")
print(parsed_file)

if isinstance(parsed_file, pd.Series):
    dfs = parsed_file.tolist()
    for i, df in enumerate(dfs):
        df.to_csv(f"/Users/annamarika/Desktop/Stage 3/text extractor/ProveTabels/tabella_{i}.csv")
else:
    with open("/Users/annamarika/Desktop/prova3colonne3.txt", 'w') as file:
        for chunk in parsed_file:
            file.write(str(chunk) + "\n")
