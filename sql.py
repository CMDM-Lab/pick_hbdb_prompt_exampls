import os
import json
import argparse
import mysql.connector

parser = argparse.ArgumentParser()
parser.add_argument('--compound_id', type=int, required=True, help='The id of the compound')
args = parser.parse_args()

# your hbdb2.sql settings
connection = mysql.connector.connect(host='localhost',
                                    port='3306',
                                    user='root',
                                    password='XXXXXXXX')
cursor = connection.cursor()

# Use `<put your database_name>`
cursor.execute("USE `hbdb2`;")

tables_dir_name = ['concept_abnormality_metadata', 'concept_chemical_metadata', 'concept_molecular function_metadata', 'concept_gene_metadata', 'concept_location_metadata', 'concept_animal model_metadata']
tables = ['concept_abnorm_metadata', 'concept_chemical_metadata', 'concept_function_metadata', 'concept_gene_metadata', 'concept_location_metadata', 'concept_model_metadata']

compound_id = args.compound_id

for idx, table in enumerate(tables):
    # print(f"idx = {idx}\n")
    cursor.execute(f"SELECT * FROM {table} WHERE `compound_id`={compound_id} AND `is_related`=1;")
    ret = cursor.fetchall()
    cursor.execute(f"SELECT `name` FROM `compounds` WHERE `id`={compound_id};")
    
    # compound name = term_A
    term_a = cursor.fetchall()[0][0]
    for i in ret:
        concept_id = i[2]
        if table == 'concept_abnorm_metadata':
            reference_id = i[7] 
            paragraph = i[5]
            sentance = i[6]
        else:
            reference_id = i[3] 
            paragraph = i[6]
            sentance = i[7]
        cursor.execute(f"SELECT `concept_name` FROM `concepts` WHERE `id`={concept_id};")

        # concept name = term_B
        term_b = cursor.fetchall()[0][0]
        print(f"now in {table}\n{compound_id}\n{concept_id}\n{reference_id}\n\n")

        cursor.execute(f"""SELECT *
                        FROM `sentences`
                        WHERE `content` 
                        LIKE '{sentance}' AND `reference_id`={reference_id};""")
        k = cursor.fetchall()
        if k == []:
            print("No results found\n")

        # the context consists of three sentences before and after the target sentence
        start_idx = k[0][0] - 3
        end_idx = k[0][0] + 3
        
        cursor.execute(f"SELECT `content` FROM `sentences` WHERE `id` BETWEEN {start_idx} AND {end_idx};")
        kk = cursor.fetchall()
        context=""
        for j in kk:
            context += j[0] + ' '

        # print(f"word_a = {word_a}\nword_b = {word_b}\ncontext = {context}\n")
        response_with_context = {
            "term_A": term_a,
            "term_B": term_b,
            "context": context
        }

        save_path = f"{term_a}/{tables_dir_name[idx]}/{reference_id}/{term_a}_{term_b}_{paragraph}.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as file:
            json.dump(response_with_context, file, indent=4)

cursor.close()
connection.close()
