import faiss
import pickle
from sentence_transformers import SentenceTransformer
from src.config import MODEL_NAME, EMBEDDINGS_INDEX_PATH, INDEX_TO_MOVIE_PATH

class VectorSearch:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = None
        self.df = None
    
    def create_embeddings(self, df):
        """Create and save embeddings for the movie dataset."""
        self.df = df
        
        # Generate embeddings
        embeddings = self.model.encode(df['text_for_embedding'].tolist(), show_progress_bar=True)
        
        # Normalize the vectors
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        
        # Save the index
        faiss.write_index(self.index, EMBEDDINGS_INDEX_PATH)
        
        # Save mapping from index position to movie
        self.index_to_movie = {i: title for i, title in enumerate(df['Series_Title'])}
        with open(INDEX_TO_MOVIE_PATH, 'wb') as f:
            pickle.dump(self.index_to_movie, f)
    
    def load_embeddings(self):
        """Load existing embeddings and index."""
        self.index = faiss.read_index(EMBEDDINGS_INDEX_PATH)
        with open(INDEX_TO_MOVIE_PATH, 'rb') as f:
            self.index_to_movie = pickle.load(f)
    
    def search(self, query, top_k=10):
        """Find similar movies based on text description."""
        if self.index is None:
            self.load_embeddings()
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search in the FAISS index
        D, I = self.index.search(query_embedding, top_k)
        
        # Format results
        results = []
        for i, (idx, score) in enumerate(zip(I[0], D[0])):
            movie_idx = int(idx)
            if movie_idx in self.index_to_movie:
                movie_row = self.df[self.df['Series_Title'] == self.index_to_movie[movie_idx]].iloc[0]
                results.append({
                    'title': movie_row['Series_Title'],
                    'year': movie_row['Released_Year'],
                    'rating': movie_row['IMDB_Rating'],
                    'genre': movie_row['Genre'],
                    'overview': movie_row['Overview'][:100] + '...',
                    'similarity_score': float(score)
                })
        
        return results 