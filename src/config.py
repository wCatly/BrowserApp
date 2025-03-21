# Neo4j Database Configuration
# Use local connection by default (change to False to use Aura cloud instance)
USE_LOCAL_NEO4J = True

# Local Neo4j (desktop/docker) configuration
LOCAL_NEO4J_URI = "neo4j://localhost:7687"
LOCAL_NEO4J_USER = "neo4j"
LOCAL_NEO4J_PASSWORD = "password"  # Change this to your local Neo4j password

# Neo4j Aura (cloud) configuration
AURA_NEO4J_URI = ""
AURA_NEO4J_USER = "neo4j"
AURA_NEO4J_PASSWORD = ""

# Set active configuration based on USE_LOCAL_NEO4J setting
if USE_LOCAL_NEO4J:
    NEO4J_URI = LOCAL_NEO4J_URI
    NEO4J_USER = LOCAL_NEO4J_USER
    NEO4J_PASSWORD = LOCAL_NEO4J_PASSWORD
else:
    NEO4J_URI = AURA_NEO4J_URI
    NEO4J_USER = AURA_NEO4J_USER
    NEO4J_PASSWORD = AURA_NEO4J_PASSWORD

# File paths
DATASET_PATH = 'data/imdb_top_1000.csv'
EMBEDDINGS_INDEX_PATH = "data/movie_embeddings.index"
INDEX_TO_MOVIE_PATH = 'data/index_to_movie.pkl'

# Model configuration
MODEL_NAME = 'all-MiniLM-L6-v2' 