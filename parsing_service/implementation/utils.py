import json


def extract_positions(paragraph):
    positions = paragraph["paragraph"]["positions"]
    return positions


def extract_minY(position):
    return position["minY"]


def extract_minX(position):
    return position["minX"]


def extract_maxY(position):
    return position["maxY"]


def extract_maxX(position):
    return position["maxX"]


def extract_role(paragraph):
    role = paragraph["paragraph"]["role"]
    return role


def extract_text(paragraph):
    text = paragraph["paragraph"]["text"]
    return text


def extract_page(paragraph):
    page = paragraph["paragraph"]["positions"][0]["page"]
    return page


def compare_paragraphs(p1, p2):
    tr = 25

    if extract_role(p1) != extract_role(p2):
        return False
    positions1, positions2 = extract_positions(p1), extract_positions(p2)

    for pos1 in positions1:
        for pos2 in positions2:
            # Compare if they are aligned with respect to the x-axis and if their distance is less than a threshold
            if (extract_minX(pos1) - extract_minX(pos2) == 0
                or extract_maxX(pos1) - extract_maxX(pos2) == 0
                or (extract_minX(pos1) + extract_maxX(pos1)) / 2 == (extract_minX(pos2) + extract_maxX(pos2)) / 2) \
                    and (extract_minY(pos1) - extract_maxY(pos2) < tr):
                return True
            # Compare if they are aligned with respect to the y-axis and if their distance is less than a threshold
            elif (extract_minY(pos1) - extract_minY(pos2) == 0
                  or extract_maxY(pos1) - extract_maxY(pos2) == 0
                  or (extract_minY(pos1) + extract_maxY(pos1)) / 2 == (extract_minY(pos2) + extract_maxY(pos2)) / 2) \
                    and (extract_minX(pos2) - extract_maxX(pos1) < tr):
                return True

    return False


def union_paragraphs(p1, p2):
    role = extract_role(p1)
    positions1 = extract_positions(p1)
    positions2 = extract_positions(p2)
    text1 = extract_text(p1)
    text2 = extract_text(p2)

    paragraph = {
        "paragraph": {
            "role": role,
            "positions": positions1 + positions2,
            "text": text1 + '\n\n' + text2
        }
    }

    return paragraph


def json_formatter(json_file):
    output = []
    i = 0
    while i < len(json_file["paragraphs"][:-1]):
        paragraph1 = json_file["paragraphs"][i]
        paragraph2 = json_file["paragraphs"][i + 1]

        if compare_paragraphs(paragraph1, paragraph2):
            paragraph = union_paragraphs(paragraph1, paragraph2)
            output.append(paragraph)

            # After merging the two paragraphs, proceed to the paragraph following the (i+1)-th one
            if i + 2 < len(json_file["paragraphs"][:-1]):
                i += 2
                continue
            # if the paragraph following the (i+1)-th one is the last one, then concatenate it
            elif i + 2 == len(json_file["paragraphs"][:-1]):
                output.append(json_file["paragraphs"][i + 2])
                break
        else:
            output.append(json_file["paragraphs"][i])

            # If the next paragraph is the last one, then concatenate it to the list of paragraphs
            if i + 1 == len(json_file["paragraphs"][:-1]):
                output.append(json_file["paragraphs"][i + 1])
        i += 1

    paragraphs = {'paragraphs': output}
    output_json = json.dumps(paragraphs, indent=2)
    return output_json


def repeat_json_formatter(json_file):
    previous_length = None
    current_json = json_file
    current_length = len(current_json["paragraphs"])

    while previous_length is None or previous_length != current_length:
        previous_length = current_length
        current_json = json.loads(json_formatter(current_json))
        current_length = len(current_json["paragraphs"])

    return current_json
