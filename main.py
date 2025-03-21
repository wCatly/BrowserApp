from tqdm import tqdm
from src.data_processor import load_and_clean_data
from src.db.graph_db import GraphDatabase
from src.db.vector_search import VectorSearch
from src.db.text_search import TextSearch
import os
import time

def clear_screen():
    """Clear the console screen."""
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For macOS and Linux
    else:
        os.system('clear')

def initialize_database():
    """Initialize the database with movie data."""
    # Load and clean data
    df = load_and_clean_data()
    
    # Initialize graph database
    graph_db = GraphDatabase()
    graph_db.clear_database()
    
    # Add movies to graph database
    print("Adding movies to graph database...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        try:
            graph_db.add_movie(row)
        except Exception as e:
            print(f"Error adding movie {row['Series_Title']}: {e}")
    
    # Initialize vector search
    vector_search = VectorSearch()
    print("Creating embeddings for vector search...")
    vector_search.create_embeddings(df)
    
    return graph_db, vector_search

def display_menu():
    """Display the main menu options."""
    print("\nSearch Options:")
    print("1. Graph DB: Find movies with actor in specific genre")
    print("2. Graph DB: Find top-rated movies by director")
    print("3. Graph DB: Find actor collaborations")
    print("4. Vector DB: Find movies similar to description")
    print("5. Full-Text: Natural language movie search")
    print("6. Initialize database (load all data)")
    print("7. Exit")

def main():
    clear_screen()
    print("Movie Search Engine - Graph vs Vector Databases")
    
    # Initialize databases
    try:
        df = load_and_clean_data()
        
        # Initialize vector search
        vector_search = VectorSearch()
        print("Creating embeddings for vector search...")
        vector_search.create_embeddings(df)
        
        # Initialize text search
        text_search = TextSearch()
        
        graph_db = GraphDatabase()  # Just connect, don't reinitialize
        

        while True:
            display_menu()
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == '1':
                clear_screen()
                print("SEARCH: MOVIES WITH ACTOR IN GENRE")
                print("==================================")
                actor = input("Enter actor name: ")
                genre = input("Enter genre: ")
                
                clear_screen()
                print(f"SEARCH RESULTS: {actor} in {genre} movies")
                print("=" * 40)
                
                results = graph_db.search("actor_genre", {"actor": actor, "genre": genre})
                
                if results:
                    print(f"\nFound {len(results)} movies with {actor} in {genre} genre:")
                    for i, r in enumerate(results[:10], 1):
                        print(f"{i}. {r['m.title']} ({r['m.year']}) - Rating: {r['m.rating']}")
                else:
                    print(f"No movies found with {actor} in {genre} genre.")
                
                input("\nPress Enter to continue...")
                clear_screen()
            
            elif choice == '2':
                clear_screen()
                print("SEARCH: TOP-RATED MOVIES BY DIRECTOR")
                print("===================================")
                director = input("Enter director name: ")
                min_rating = float(input("Enter minimum rating (0-10): "))
                
                clear_screen()
                print(f"SEARCH RESULTS: {director}'s movies rated ≥ {min_rating}")
                print("=" * 50)
                
                results = graph_db.search("director_rating", {"director": director, "min_rating": min_rating})
                
                if results:
                    print(f"\nFound {len(results)} movies by {director} with rating ≥ {min_rating}:")
                    for i, r in enumerate(results[:10], 1):
                        print(f"{i}. {r['m.title']} ({r['m.year']}) - Rating: {r['m.rating']}")
                else:
                    print(f"No movies found by {director} with rating ≥ {min_rating}.")
                
                input("\nPress Enter to continue...")
                clear_screen()
            
            elif choice == '3':
                clear_screen()
                print("SEARCH: ACTOR COLLABORATIONS")
                print("============================")
                actor = input("Enter actor name: ")
                
                clear_screen()
                print(f"SEARCH RESULTS: {actor}'s top collaborators")
                print("=" * 40)
                
                results = graph_db.search("actor_collaboration", {"actor": actor})
                
                if results:
                    print(f"\nTop collaborators with {actor}:")
                    for i, r in enumerate(results[:10], 1):
                        print(f"{i}. {r['actor']} - Collaborated in {r['collaboration_count']} movies")
                else:
                    print(f"No collaborations found for {actor}.")
                
                input("\nPress Enter to continue...")
                clear_screen()
            
            elif choice == '4':
                clear_screen()
                print("SEARCH: MOVIES SIMILAR TO DESCRIPTION")
                print("====================================")
                description = input("Enter movie description or keywords: ")
                
                clear_screen()
                print(f"SEARCH RESULTS: Movies similar to your description")
                print("=" * 50)
                print(f"Query: \"{description}\"")
                print()
                
                results = vector_search.search(description, top_k=10)
                
                if results:
                    print(f"Found {len(results)} similar movies:")
                    for i, r in enumerate(results[:10], 1):
                        print(f"{i}. {r['title']} ({r['year']}) - {r['genre']}")
                        print(f"   Overview: {r['overview']}")
                        print(f"   Similarity score: {r['similarity_score']:.3f}")
                else:
                    print("No similar movies found.")
                
                input("\nPress Enter to continue...")
                clear_screen()
            
            elif choice == '5':
                clear_screen()
                print("NATURAL LANGUAGE MOVIE SEARCH")
                print("=============================")
                query = input("What kind of movie would you like to watch? ")
                
                clear_screen()
                print("MOVIE RECOMMENDATIONS")
                print("====================")
                print(f"Query: \"{query}\"")
                
                # Get detected genres (if any)
                genres = text_search.extract_genre(query)
                if genres:
                    print(f"Detected genres: {', '.join(genres)}")
                print()
                
                results = text_search.search(query, top_k=10)
                
                if results:
                    print(f"Here are some recommendations based on your request:")
                    for i, r in enumerate(results[:10], 1):
                        print(f"{i}. {r['title']} ({r['year']}) - {r['genre']}")
                        print(f"   Overview: {r['overview']}")
                        print(f"   Similarity score: {r['similarity_score']:.3f}")
                else:
                    print("No matching movies found.")
                
                input("\nPress Enter to continue...")
                clear_screen()
            
            elif choice == '6':
                clear_screen()
                print("INITIALIZING DATABASE")
                print("====================")
                print("This may take several minutes. Please wait...")
                graph_db.close()  # Close the current connection
                graph_db, vector_search = initialize_database()
                # Recreate text search with new vector search
                text_search = TextSearch()
                print("\nDatabase initialized successfully!")
                
                input("\nPress Enter to continue...")
                clear_screen()
            
            elif choice == '7':
                clear_screen()
                print("Thank you for using the Movie Search Engine!")
                time.sleep(1.5)
                break
            
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)
                clear_screen()
    finally:
        # Make sure to close the database connection when exiting
        if 'graph_db' in locals():
            graph_db.close()

if __name__ == "__main__":
    main() 