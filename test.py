from parsing_service.implementation.parser_factory import parse_file, parse_file_to_json
import json
import os


def write_paragraphs_to_file(save_path, json_data, filename):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = os.path.join(save_path, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        paragraphs = json_data['paragraphs']
        for index, item in enumerate(paragraphs):
            paragraph = item['paragraph']
            role = paragraph['role']
            text = paragraph['text']
            page = paragraph['positions'][0]['page']
            file.write("Role: " + role + '\n' + text + '\n' + "Page: " + str(page) + '\n\n')

            if index < len(paragraphs[:-1]):
                file.write('\n' + '-' * 80 + '\n\n')


path = "/Users/annamarika/PycharmProjects/text-extractor/samples/base.pdf"

# il file json è già salvato nel path indicato
parsed_file = parse_file_to_json(path, "pdf")
print(parsed_file)

# salvo il json in una cartella che voglio io
with open(f"/Users/annamarika/Desktop/prova.json", 'w') as file:
    json.dump(parsed_file, file, indent=2)

# apro il file json e lo scrivo in un txt per visualizzarlo meglio
with open("/Users/annamarika/Desktop/prova.json", 'r') as file:
    formatted_json_data = json.load(file)

write_paragraphs_to_file("/Users/annamarika/Desktop", formatted_json_data, "Circular EconomyFormatted.txt")

"""if isinstance(parsed_file, pd.Series):
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
            file.write(str(chunk) + "\n")"""
