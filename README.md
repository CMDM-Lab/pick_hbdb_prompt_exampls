# HBDB Compound Search

A Flask web application for searching and analyzing compound relationships in the HBDB database.

## Prerequisites

- Python 3.10
- Docker and Docker Compose
- MySQL 8.0

## Quick Start with Docker

1. Clone the repository

2. Create a `.env` file in the root directory with the following variables:
```bash
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=hbdb2
```

3. Place your `hbdb2.sql` file in the root directory

4. Build and run the containers:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:5020`

## Manual Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure MySQL:
- Install MySQL 8.0
- Create a database named `hbdb2`
- Import the `hbdb2.sql` file

4. Set up environment variables:
- Create a `.env` file with the same variables as shown in the Docker setup
- Adjust MYSQL_HOST to `localhost` for local development

5. Run the application:
```bash
python app.py
```

## Usage

1. Access the web interface at `http://localhost:5020`
2. Enter a compound ID in the search form
3. View the results showing:
   - Compound name
   - Related terms
   - Context information
   - Category classifications

## Downloading Results

The application generates JSON files for each compound-concept relationship. These files are stored in the following structure:

```
{compound_name}/
    ├── concept_abnormality_metadata/
    ├── concept_chemical_metadata/
    ├── concept_molecular function_metadata/
    ├── concept_gene_metadata/
    ├── concept_location_metadata/
    └── concept_animal model_metadata/
```

Each JSON file follows the naming format:
```
{compound_name}_{term_B}_{paragraph}.json
```

To download the JSON files:

1. After searching for a compound, the files will be generated in the appropriate directories
2. Access the files directly from the project directory
3. Each JSON file contains:
   ```json
   {
       "term_A": "compound name",
       "term_B": "related concept",
       "context": "surrounding text including the target sentence",
       "category": "concept category"
   }
   ```

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
- `docker-compose.yml`: Docker services configuration
- `Dockerfile`: Web application container configuration
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (create this)
- `hbdb2.sql`: Database schema and data (provide this)

## Environment Variables

- `MYSQL_HOST`: MySQL server hostname
- `MYSQL_PORT`: MySQL server port
- `MYSQL_USER`: MySQL username
- `MYSQL_ROOT_PASSWORD`: MySQL root password
- `MYSQL_DATABASE`: Database name (hbdb2)
