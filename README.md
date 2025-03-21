# Movie Search Engine

A hybrid search engine for movies that demonstrates the power of both graph databases and vector search using the IMDB Top 1000 Movies dataset.

## Features

- **Graph Database Searches**:
  - Find movies with specific actors in particular genres
  - Discover top-rated movies by directors
  - Explore actor collaborations and connections

- **Vector Search**:
  - Find movies similar to a description or concept
  - Semantic search based on content similarity

- **Natural Language Movie Recommendations**:
  - Ask for movies in conversational language
  - Automatic genre detection from queries
  - Smart ranking based on intent and content

## Project Architecture

The project is organized into the following components:

```
movie-search-engine/
├── data/                    # Data files
│   ├── imdb_top_1000.csv    # Movie dataset
│   └── ... (index files)
├── src/                     # Core functionality
│   ├── db/                  # Database modules
│   │   ├── graph_db.py      # Neo4j graph database interface
│   │   ├── vector_search.py # FAISS vector search implementation
│   │   └── text_search.py   # Natural language search
│   └── data_processor.py    # Data cleaning and processing
├── scripts/                 # Utility scripts
│   ├── demo_search.py       # Demo of all search capabilities
│   ├── setup_local_neo4j.py # Script to set up Neo4j in Docker
│   └── ... (other scripts)
└── main.py                  # Main application
```

## Prerequisites

- Python 3.8+
- Neo4j (local instance or cloud service)
- FAISS for vector search
- Docker (optional, for automatic Neo4j setup)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd movie-search-engine
   ```

2. Install dependencies (choose one method):
   
   **Option 1: Using setup.py (recommended)**
   ```bash
   pip install -e .
   ```
   
   **Option 2: Using requirements.txt**
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Neo4j:

   **Option 1: Automated Setup with Docker (recommended)**
   ```bash
   python3 scripts/setup_local_neo4j.py
   ```
   This script will:
   - Check if Docker is installed
   - Create and start a Neo4j Docker container
   - Configure the correct password
   - Update your config.py file automatically
   
   **Option 2: Manual Setup**
   - Install Neo4j locally or set up a cloud instance
   - Update connection details in `src/config.py`

## Docker Setup Details

The `setup_local_neo4j.py` script provides an easy way to set up Neo4j using Docker:

### What it Does

1. **Creates a Docker Container**: Sets up a Neo4j container named `movie-neo4j`
2. **Configures Ports**: Exposes Neo4j on standard ports (7474 for browser, 7687 for Bolt)
3. **Creates Persistent Volume**: Ensures your data persists between restarts
4. **Sets Password**: Configures the Neo4j password
5. **Updates Config**: Automatically updates your `config.py` file

### Requirements

- Docker installed and running
- Ports 7474 and 7687 available

### Access Neo4j Browser

After running the setup script, you can access the Neo4j browser at:
```
http://localhost:7474
```

Login with:
- Username: `neo4j`
- Password: `password` (or whatever you provided during setup)

## Usage

### Running the Application

```bash
python3 main.py
```

### Running the Demo

To see a demonstration of all search capabilities with sample queries:

```bash
python3 scripts/demo_search.py
```

## Search Examples

### Graph DB: Actor in Genre Search
```
Query: Actor: "Morgan Freeman", Genre: "Drama"
Result: The Shawshank Redemption, Se7en, Glory, etc.
```

### Graph DB: Director with Rating Threshold
```
Query: Director: "Christopher Nolan", Min Rating: 8.0
Result: The Dark Knight, Inception, Interstellar, etc.
```

### Graph DB: Actor Collaborations
```
Query: Actor: "Robert De Niro"
Result: Top collaborators include Joe Pesci (4 films), Al Pacino (3 films), etc.
```

### Vector Search: Similar Movie Descriptions
```
Query: "Mafia family drama with excellent acting"
Result: The Godfather, Goodfellas, Donnie Brasco, etc.
```

### Natural Language Search
```
Query: "I want to watch some drama movie today"
Result: Automatically detects "drama" genre and returns top drama films
```

## How It Works

1. **Graph Database (Neo4j)**
   - Stores relationships between movies, actors, directors, and genres
   - Enables complex relationship queries (e.g., actor collaborations)
   - Provides fast traversal of movie relationships

2. **Vector Search (FAISS)**
   - Converts movie descriptions and metadata into embeddings
   - Enables semantic similarity search
   - Powered by sentence-transformers

3. **Natural Language Processing**
   - Combines vector search with intent detection
   - Extracts genre keywords from natural language
   - Provides conversational movie recommendations

## Data

The project uses the [IMDB Top 1000 Movies and TV Shows dataset from Kaggle](https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows?resource=download), which includes:
- Movie titles, release years, and ratings
- Director and main cast information
- Genre classifications
- Plot overviews and other metadata

## Troubleshooting

### Neo4j Connection Issues

If you experience problems connecting to Neo4j:

1. **Check if Neo4j is running:**
   ```bash
   # If using Docker
   docker ps | grep neo4j
   ```

2. **Verify Neo4j credentials:**
   - Ensure the credentials in `src/config.py` match your Neo4j setup
   - Default credentials for the Docker setup are:
     - Username: `neo4j`
     - Password: `password` (or the one you provided during setup)

3. **Test Neo4j connection directly:**
   ```bash
   python3 scripts/test_connection.py
   ```

4. **Neo4j container issues:**
   If the Docker container isn't working properly:
   ```bash
   # Stop and remove the container
   docker stop movie-neo4j
   docker rm movie-neo4j
   
   # Then run the setup script again
   python3 scripts/setup_local_neo4j.py
   ```

### Vector Search Issues

If vector search isn't working:

1. **Check the embeddings files:**
   - Ensure `data/movie_embeddings.index` and `data/index_to_movie.pkl` exist
   - If missing, run the application and select option 6 to initialize the database

2. **FAISS installation issues:**
   If you encounter errors with FAISS:
   ```bash
   pip uninstall faiss-cpu
   pip install faiss-cpu --no-cache-dir
   ```


 