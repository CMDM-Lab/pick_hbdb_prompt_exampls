from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap5
import os
import json
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
bootstrap = Bootstrap5(app) 

def process_compound_data(compound_id):
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_ROOT_PASSWORD')
    )
    cursor = connection.cursor()
    cursor.execute("USE `hbdb2`;")
    
    # Get compound name
    cursor.execute(f"SELECT `name` FROM `compounds` WHERE `id`={compound_id};")
    result = cursor.fetchone()
    if not result:
        return None
    
    compound_name = result[0]
    
    # Define tables as in original sql.py
    tables_dir_name = ['concept_abnormality_metadata', 'concept_chemical_metadata', 
                      'concept_molecular function_metadata', 'concept_gene_metadata', 
                      'concept_location_metadata', 'concept_animal model_metadata']
    tables = ['concept_abnorm_metadata', 'concept_chemical_metadata', 
              'concept_function_metadata', 'concept_gene_metadata', 
              'concept_location_metadata', 'concept_model_metadata']
    
    results = []
    
    for idx, table in enumerate(tables):
        cursor.execute(f"SELECT * FROM {table} WHERE `compound_id`={compound_id} AND `is_related`=1;")
        ret = cursor.fetchall()
        
        for i in ret:
            concept_id = i[2]
            if table == 'concept_abnorm_metadata':
                reference_id = i[7]
                paragraph = i[5]
                sentence = i[6]
            else:
                reference_id = i[3]
                paragraph = i[6]
                sentence = i[7]
                
            cursor.execute(f"SELECT `concept_name` FROM `concepts` WHERE `id`={concept_id};")
            term_b = cursor.fetchall()[0][0]
            
            # Get context sentences
            # Escape single quotes in the sentence
            escaped_sentence = sentence.replace("'", "''")
            cursor.execute(f"""SELECT *
                            FROM `sentences`
                            WHERE `content` 
                            LIKE %s AND `reference_id`=%s;""", (escaped_sentence, reference_id))
            k = cursor.fetchall()
            if k:
                start_idx = k[0][0] - 3
                end_idx = k[0][0] + 3
                
                cursor.execute(f"SELECT `content` FROM `sentences` WHERE `id` BETWEEN %s AND %s;", 
                             (start_idx, end_idx))
                kk = cursor.fetchall()
                context = " ".join(j[0] for j in kk)
                
                # Store result
                result_data = {
                    "term_A": compound_name,
                    "term_B": term_b,
                    "context": context,
                    "category": tables_dir_name[idx],
                    "score": None,  # Default score
                    "verified": False,  # Default verification status
                    "table": table,
                    "compound_id": compound_id,
                    "concept_id": concept_id,
                    "reference_id": reference_id,
                    "paragraph": paragraph
                }
                
                # Save to file
                save_path = f"{compound_name}/{tables_dir_name[idx]}/{reference_id}"
                os.makedirs(save_path, exist_ok=True)
                file_path = f"{save_path}/{compound_name}_{term_b}_{paragraph}.json"
                with open(file_path, "w") as file:
                    json.dump(result_data, file, indent=4)
                
                results.append(result_data)
    
    cursor.close()
    connection.close()
    
    return {
        'compound_name': compound_name,
        'results': results
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    error = None
    
    if request.method == 'POST':
        try:
            compound_id = int(request.form.get('compound_id'))
            data = process_compound_data(compound_id)
            if not data:
                error = f"No compound found with ID {compound_id}"
        except ValueError:
            error = "Please enter a valid compound ID (number)"
        except Exception as e:
            error = f"An error occurred: {str(e)}"
    
    return render_template('index.html', data=data, error=error)

@app.route('/update_score', methods=['POST'])
def update_score():
    try:
        data = request.json
        compound_name = data['compound_name']
        term_b = data['term_b']
        category = data['category']
        reference_id = data['reference_id']
        paragraph = data['paragraph']
        score = data['score']
        verified = data['verified']
        
        # Construct the file path
        file_path = f"{compound_name}/{category}/{reference_id}/{compound_name}_{term_b}_{paragraph}.json"
        
        # Read existing JSON
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        
        # Update score and verification
        json_data['score'] = score
        json_data['verified'] = verified
        
        # Save updated JSON
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/list_files')
def list_files():
    try:
        compounds = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
        all_files = []
        sections = set()
        terms_a = set()
        verified_count = 0
        scored_count = 0
        
        for compound in compounds:
            for category in os.listdir(compound):
                category_path = os.path.join(compound, category)
                if os.path.isdir(category_path):
                    for ref_id in os.listdir(category_path):
                        ref_path = os.path.join(category_path, ref_id)
                        if os.path.isdir(ref_path):
                            for file in os.listdir(ref_path):
                                if file.endswith('.json'):
                                    file_path = os.path.join(ref_path, file)
                                    with open(file_path, 'r') as f:
                                        data = json.load(f)
                                        if data.get('score'):
                                            scored_count += 1
                                        if data.get('verified'):
                                            verified_count += 1
                                        # Extract paragraph name from filename
                                        paragraph_name = file.split('_')[-1].replace('.json', '')

                                        file_info = {
                                            'path': file_path,
                                            'compound': compound,
                                            'category': category,
                                            'reference_id': ref_id,
                                            'term_A': data.get('term_A', ''),
                                            'term_B': data.get('term_B', ''),
                                            'context': data.get('context', ''),
                                            'score': int(data.get('score')) if data.get('score') else None,  # Convert to integer
                                            'verified': data.get('verified', False),
                                            'paragraph': paragraph_name
                                        }
                                        all_files.append(file_info)
                                        sections.add(file_info['paragraph'])
                                        terms_a.add(file_info['term_A'])
        
        return render_template('list_files.html', 
                             files=all_files,
                             sections=sorted(sections),
                             terms_a=sorted(terms_a),
                             verified_count=verified_count,
                             scored_count=scored_count,
                             total_count=len(all_files))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/needs_verification', methods=['GET'])
def needs_verification():
    try:
        # Get all compound directories
        compounds = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
        files_to_verify = []
        
        for compound in compounds:
            for category in os.listdir(compound):
                category_path = os.path.join(compound, category)
                if os.path.isdir(category_path):
                    for ref_id in os.listdir(category_path):
                        ref_path = os.path.join(category_path, ref_id)
                        if os.path.isdir(ref_path):
                            for file in os.listdir(ref_path):
                                if file.endswith('.json'):
                                    file_path = os.path.join(ref_path, file)
                                    with open(file_path, 'r') as f:
                                        data = json.load(f)
                                        # Check if file has score but isn't verified
                                        if data.get('score') and not data.get('verified', False):
                                            paragraph_name = file.split('_')[-1].replace('.json', '')
                                            file_info = {
                                                'path': file_path,
                                                'compound': compound,
                                                'category': category,
                                                'reference_id': ref_id,
                                                'term_A': data.get('term_A', ''),
                                                'term_B': data.get('term_B', ''),
                                                'context': data.get('context', ''),
                                                'score': int(data.get('score')) if data.get('score') else None,
                                                'verified': data.get('verified', False),
                                                'paragraph': paragraph_name
                                            }
                                            files_to_verify.append(file_info)
        
        return render_template('needs_verification.html', files=files_to_verify)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_verified', methods=['GET'])
def download_verified():
    try:
        # Create a BytesIO object to store the zip file
        memory_file = BytesIO()
        
        # Create a ZipFile object
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            compounds = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
            
            for compound in compounds:
                for category in os.listdir(compound):
                    category_path = os.path.join(compound, category)
                    if os.path.isdir(category_path):
                        for ref_id in os.listdir(category_path):
                            ref_path = os.path.join(category_path, ref_id)
                            if os.path.isdir(ref_path):
                                for file in os.listdir(ref_path):
                                    if file.endswith('.json'):
                                        file_path = os.path.join(ref_path, file)
                                        with open(file_path, 'r') as f:
                                            data = json.load(f)
                                            # Check if file has score and is verified
                                            if data.get('score') and data.get('verified', False):
                                                # Add file to zip with its relative path
                                                zf.write(file_path, os.path.join(compound, category, ref_id, file))
        
        # Reset the file pointer
        memory_file.seek(0)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'verified_files_{timestamp}.zip'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5020, debug=True) 