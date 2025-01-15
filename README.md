# hbdb2 construct context

## First step
Download the `hbdb2.sql`

## Environment Setup
Create a new conda environment
```bash
conda create --name hbdb_env python=3.10
```
Activate the conda environment
```bash
conda activate hbdb_env
```
Install necessary package
```bash
pip insall mysql-connector-python==9.1.0
```

## Modify `sql.py` to match your dataset format
Replace the following line in the script with your own MySQL settings:
```bash
connection = mysql.connector.connect(host='localhost', port='3306',user='root'password='XXXXXXXX')
```
Ensure the host, port, user, and password match your database configuration.

- host: The hostname or IP address of your MySQL server.
- port: The port number your MySQL server listens on (default is 3306).
- user: Your MySQL username.
- password: Your MySQL password (replace XXXXXXXX with the actual password).

## Construct context
Run the `sql.py` script with the specified `compound_id` parameter.

As an example, using compound "acetone," replace 28 with the desired compound ID to fetch data from the database:
```bash
python sql.py --compound_id 28
```

## Results
The results will be stored in a directory named after the compound name.

The JSON files will follow this naming format:
```bash
{term_A}_{term_B}_{paragraph}.json
```

Each JSON file will have the following structure:
```bash
{
    "term_A": "value of term A",
    "term_B": "value of term B",
    "context": "surrounding text including the target sentence"
}
```
