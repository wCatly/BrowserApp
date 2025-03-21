from src.data_processor import load_and_clean_data
from src.db.graph_db import GraphDatabase
from src.db.vector_search import VectorSearch
from src.db.text_search import TextSearch
import time

def run_demo():
    """Run a demonstration of all search options with sample inputs."""
    print("Movie Search Engine - Demo Mode")
    print("===============================\n")
    
    # Load data
    print("Loading data...")
    df = load_and_clean_data()
    print(f"Loaded {len(df)} movies from dataset\n")
    
    # Initialize vector search
    print("Initializing vector search...")
    vector_search = VectorSearch()
    vector_search.create_embeddings(df)
    
    # Initialize text search
    text_search = TextSearch()
    
    # Connect to graph database
    print("Connecting to graph database...\n")
    graph_db = GraphDatabase()
    
    # Demo 1: Actor in Genre searches
    print("\n1. GRAPH DB: ACTORS IN GENRES")
    print("=============================")
    actor_genre_examples = [
        {"actor": "Tom Hanks", "genre": "Drama"},
        {"actor": "Leonardo DiCaprio", "genre": "Crime"},
        {"actor": "Meryl Streep", "genre": "Comedy"},
        {"actor": "Morgan Freeman", "genre": "Drama"}
    ]
    
    for example in actor_genre_examples:
        print(f"\nSearching for movies with {example['actor']} in {example['genre']} genre:")
        results = graph_db.search("actor_genre", example)
        if results:
            print(f"Found {len(results)} movies:")
            for i, r in enumerate(results[:5], 1):
                print(f"{i}. {r['m.title']} ({r['m.year']}) - Rating: {r['m.rating']}")
            if len(results) > 5:
                print(f"... and {len(results)-5} more")
        else:
            print(f"No movies found with {example['actor']} in {example['genre']} genre.")
        time.sleep(1)
    
    # Demo 2: Directors with high ratings
    print("\n\n2. GRAPH DB: TOP-RATED MOVIES BY DIRECTORS")
    print("==========================================")
    director_examples = [
        {"director": "Christopher Nolan", "min_rating": 8.0},
        {"director": "Quentin Tarantino", "min_rating": 8.5},
        {"director": "Steven Spielberg", "min_rating": 8.0},
        {"director": "Martin Scorsese", "min_rating": 8.5}
    ]
    
    for example in director_examples:
        print(f"\nSearching for movies by {example['director']} with rating ≥ {example['min_rating']}:")
        results = graph_db.search("director_rating", example)
        if results:
            print(f"Found {len(results)} movies:")
            for i, r in enumerate(results[:5], 1):
                print(f"{i}. {r['m.title']} ({r['m.year']}) - Rating: {r['m.rating']}")
            if len(results) > 5:
                print(f"... and {len(results)-5} more")
        else:
            print(f"No movies found by {example['director']} with rating ≥ {example['min_rating']}.")
        time.sleep(1)
    
    # Demo 3: Actor collaborations
    print("\n\n3. GRAPH DB: ACTOR COLLABORATIONS")
    print("=================================")
    actor_examples = [
        "Leonardo DiCaprio", 
        "Tom Hanks", 
        "Meryl Streep",
        "Robert De Niro"
    ]
    
    for actor in actor_examples:
        print(f"\nFinding top collaborators with {actor}:")
        results = graph_db.search("actor_collaboration", {"actor": actor})
        if results:
            print(f"Top collaborators:")
            for i, r in enumerate(results[:5], 1):
                print(f"{i}. {r['actor']} - Collaborated in {r['collaboration_count']} movies")
            if len(results) > 5:
                print(f"... and {len(results)-5} more")
        else:
            print(f"No collaborations found for {actor}.")
        time.sleep(1)
    
    # Demo 4: Vector searches
    print("\n\n4. VECTOR DB: SEMANTIC MOVIE SEARCHES")
    print("=====================================")
    description_examples = [
        "Mafia family drama with excellent acting",
        "Space adventure with amazing visuals",
        "Psychological thriller with plot twists",
        "War movie showing the horrors of combat"
    ]
    
    for desc in description_examples:
        print(f"\nSearching for movies similar to: '{desc}'")
        results = vector_search.search(desc, top_k=5)
        if results:
            print(f"Found similar movies:")
            for i, r in enumerate(results[:5], 1):
                print(f"{i}. {r['title']} ({r['year']}) - {r['genre']}")
                print(f"   Overview: {r['overview']}")
                print(f"   Similarity score: {r['similarity_score']:.3f}")
        else:
            print("No similar movies found.")
        time.sleep(1)
    
    # Demo 5: Full-text natural language search
    print("\n\n5. FULL-TEXT: NATURAL LANGUAGE SEARCH")
    print("=====================================")
    query_examples = [
        "I want to watch some drama movie today",
        "Looking for an action movie with explosions",
        "I need a good comedy to cheer me up",
        "Show me sci-fi movies about space travel"
    ]
    
    for query in query_examples:
        print(f"\nQuery: '{query}'")
        
        # Get detected genres (if any)
        genres = text_search.extract_genre(query)
        if genres:
            print(f"Detected genres: {', '.join(genres)}")
        
        results = text_search.search(query, top_k=5)
        if results:
            print(f"Recommended movies:")
            for i, r in enumerate(results[:5], 1):
                print(f"{i}. {r['title']} ({r['year']}) - {r['genre']}")
                print(f"   Overview: {r['overview']}")
                print(f"   Similarity score: {r['similarity_score']:.3f}")
        else:
            print("No matching movies found.")
        time.sleep(1)
    
    # Close connection
    print("\n\nDemo complete!")
    graph_db.close()

if __name__ == "__main__":
    run_demo() 