import os
import json

def remove_duplicates(questions):
    unique_questions = []
    for question in questions:
        if question not in unique_questions:
            unique_questions.append(question)
    return unique_questions

def merge_json_files(directory):
    merged_data = {"thematique": "", "questions": []}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r", encoding='utf-8') as file:
                data = json.load(file)
                merged_data["thematique"] = data["thematique"]
                merged_data["questions"].extend(remove_duplicates(data["questions"]))
    return merged_data

def write_json_file(data, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


    
if __name__ == "__main__":
    directory = "questions/humanitaire"
    output_file = "humanitaire.json"
    all_questions = []    
    with open(os.path.join(directory, output_file), 'r', encoding='utf-8') as file:
            data_json = json.load(file)
            all_questions.extend(data_json['questions'])
            
    print(len(all_questions))

    # merged_data = merge_json_files(directory)
    # write_json_file(merged_data, output_file)
    # print("Les doublons ont été supprimés avec succès.")

    