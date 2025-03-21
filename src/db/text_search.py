import re
from src.db.vector_search import VectorSearch
from src.db.graph_db import GraphDatabase
from src.data_processor import load_and_clean_data

class TextSearch:
    """Enhanced text search that combines vector search with intent extraction"""
    
    # Common movie genres to detect in queries
    GENRES = [
        "action", "adventure", "animation", "biography", "comedy", "crime", 
        "documentary", "drama", "family", "fantasy", "film-noir", "history", 
        "horror", "music", "musical", "mystery", "romance", "sci-fi", "sport", 
        "thriller", "war", "western"
    ]
    
    def __init__(self):
        # Load the data
        self.df = load_and_clean_data()
        
        # Initialize vector search
        self.vector_search = VectorSearch()
        
        # Make sure vector search has embeddings ready
        # If the index doesn't exist, create it
        if self.vector_search.index is None:
            try:
                self.vector_search.load_embeddings()
                # Make sure df is available for vector search
                self.vector_search.df = self.df
            except:
                print("Creating new embeddings...")
                self.vector_search.create_embeddings(self.df)
        
        self.graph_db = GraphDatabase()
    
    def extract_genre(self, query):
        """Extract genre mentions from a natural language query"""
        # Convert to lowercase for matching
        query_lower = query.lower()
        
        # Find all mentioned genres
        mentioned_genres = []
        for genre in self.GENRES:
            if genre in query_lower:
                # Capitalize first letter of each word in multi-word genres
                formatted_genre = '-'.join(word.capitalize() for word in genre.split('-'))
                mentioned_genres.append(formatted_genre)
                
        return mentioned_genres
    
    def search(self, query, top_k=10):
        """Search for movies based on natural language query"""
        # Extract any genres mentioned in the query
        mentioned_genres = self.extract_genre(query)
        
        # Make sure vector search has the dataframe
        if self.vector_search.df is None:
            self.vector_search.df = self.df
        
        # Get vector search results
        vector_results = self.vector_search.search(query, top_k=top_k*2)  # Get more results than needed
        
        if not mentioned_genres:
            # No specific genre mentioned, just return vector results
            return vector_results[:top_k]
            
        # Filter and rerank results based on genre
        final_results = []
        genre_matches = []
        non_matches = []
        
        for result in vector_results:
            # Check if the movie's genre matches any of the mentioned genres
            movie_genres = [g.strip() for g in result['genre'].split(',')]
            if any(genre in movie_genres for genre in mentioned_genres):
                # Boost similarity score for genre matches
                result['similarity_score'] += 0.2  # Boost the score
                genre_matches.append(result)
            else:
                non_matches.append(result)
        
        # Sort genre matches by similarity score
        genre_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        non_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Combine results, prioritizing genre matches
        final_results = genre_matches + non_matches
        
        return final_results[:top_k] 