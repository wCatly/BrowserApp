from neo4j import GraphDatabase as Neo4jDriver
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import pandas as pd

class GraphDatabase:
    def __init__(self):
        self.driver = Neo4jDriver.driver(
            NEO4J_URI, 
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            connection_timeout=5,  # 5 second connection timeout
            max_connection_lifetime=20  # 20 second connection lifetime
        )
        self._setup_constraints()
    
    def _setup_constraints(self):
        """Set up database constraints."""
        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT movie_title IF NOT EXISTS FOR (m:Movie) REQUIRE m.title IS UNIQUE")
                session.run("CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE")
                session.run("CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE")
            except Exception as e:
                print(f"Warning: Error setting up constraints: {e}")
                try:
                    session.run("CREATE CONSTRAINT ON (m:Movie) ASSERT m.title IS UNIQUE")
                    session.run("CREATE CONSTRAINT ON (p:Person) ASSERT p.name IS UNIQUE")
                    session.run("CREATE CONSTRAINT ON (g:Genre) ASSERT g.name IS UNIQUE")
                except Exception as e2:
                    print(f"Warning: Failed to create constraints with Neo4j 4.x syntax too: {e2}")
                # Continue anyway, as the constraints might already exist
    
    def clear_database(self):
        """Clear all existing data."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def add_movie(self, row):
        """Add a movie and its relationships to the graph database."""
        try:
            # Pre-process row data to ensure all required fields are available
            # Handle No_of_Votes specifically as it's causing issues
            if 'No_of_votes' not in row or pd.isna(row['No_of_votes']) or row['No_of_votes'] == '':
                row['No_of_votes'] = 0
                
            with self.driver.session() as session:
                session.execute_write(self._add_movie_tx, row)
                
        except Exception as e:
            print(f"Error adding movie {row.get('Series_Title', 'Unknown')}: {str(e)}")
            # Continue with next movie
    
    def _add_movie_tx(self, tx, row):
        """Transaction function to add a movie and its relationships."""
        # Create Movie node with safer conversions
        movie_props = {
            "title": str(row['Series_Title']),
            "year": int(float(row['Released_Year'])) if row['Released_Year'] and str(row['Released_Year']).strip() and str(row['Released_Year']).strip().lower() != 'nan' else None,
            "rating": float(row['IMDB_Rating']) if row['IMDB_Rating'] and str(row['IMDB_Rating']).strip() and str(row['IMDB_Rating']).strip().lower() != 'nan' else None,
            "runtime": row['Runtime'] if row['Runtime'] else '',
            "overview": str(row['Overview']) if row['Overview'] else '',
            "metascore": float(row['Meta_score']) if row['Meta_score'] and str(row['Meta_score']).strip() and str(row['Meta_score']).strip().lower() != 'nan' else None,
            "votes": int(float(row['No_of_votes'])) if row['No_of_votes'] and str(row['No_of_votes']).strip() and str(row['No_of_votes']).strip().lower() != 'nan' else 0,
            "gross": str(row['Gross']) if row['Gross'] else '',
            "certificate": str(row['Certificate']) if row['Certificate'] else '',
            "poster_link": str(row['Poster_Link']) if row['Poster_Link'] else ''
        }
        
        # Create the movie node
        create_movie_query = """
        MERGE (m:Movie {title: $title})
        ON CREATE SET m += $props
        RETURN m
        """
        movie_result = tx.run(create_movie_query, title=movie_props["title"], props=movie_props).single()
        
        # Create Director node and relationship
        if row['Director'] and str(row['Director']).strip():
            create_director_query = """
            MERGE (p:Person {name: $name, role: 'Director'})
            WITH p
            MATCH (m:Movie {title: $movie_title})
            MERGE (p)-[:DIRECTED]->(m)
            """
            tx.run(create_director_query, name=str(row['Director']), movie_title=str(row['Series_Title']))
        
        # Create Stars nodes and relationships
        for i in range(1, 5):
            star_col = f'Star{i}'
            if row[star_col] and str(row[star_col]).strip():
                create_star_query = """
                MERGE (p:Person {name: $name, role: 'Actor'})
                WITH p
                MATCH (m:Movie {title: $movie_title})
                MERGE (p)-[:ACTED_IN]->(m)
                MERGE (m)-[:CAST]->(p)
                """
                tx.run(create_star_query, name=str(row[star_col]), movie_title=str(row['Series_Title']))
        
        # Create Genre nodes and relationships
        if row['Genre'] and str(row['Genre']).strip():
            genres = [genre.strip() for genre in str(row['Genre']).split(',')]
            for genre_name in genres:
                if genre_name.strip():
                    create_genre_query = """
                    MERGE (g:Genre {name: $name})
                    WITH g
                    MATCH (m:Movie {title: $movie_title})
                    MERGE (m)-[:IN_GENRE]->(g)
                    MERGE (g)-[:HAS_MOVIE]->(m)
                    """
                    tx.run(create_genre_query, name=genre_name, movie_title=str(row['Series_Title']))
    
    def search(self, query_type, params):
        """Execute graph-based searches in Neo4j."""
        with self.driver.session() as session:
            # Trim any input parameters that are strings to handle extra spaces
            for key in params:
                if isinstance(params[key], str):
                    params[key] = params[key].strip()
            
            if query_type == "actor_genre":
                cypher_query = """
                MATCH (a:Person {name: $actor_name, role: 'Actor'})-[:ACTED_IN]->(m:Movie)-[:IN_GENRE]->(g:Genre {name: $genre_name})
                RETURN m.title as `m.title`, m.year as `m.year`, m.rating as `m.rating`
                ORDER BY m.rating DESC
                """
                return session.run(cypher_query, actor_name=params['actor'], genre_name=params['genre']).data()
            
            elif query_type == "director_rating":
                cypher_query = """
                MATCH (d:Person {name: $director_name, role: 'Director'})-[:DIRECTED]->(m:Movie)
                WHERE m.rating >= $min_rating
                RETURN m.title as `m.title`, m.year as `m.year`, m.rating as `m.rating`
                ORDER BY m.rating DESC
                """
                return session.run(cypher_query, 
                                  director_name=params['director'], 
                                  min_rating=params.get('min_rating', 7.0)).data()
            
            elif query_type == "actor_collaboration":
                cypher_query = """
                MATCH (a1:Person {name: $actor_name, role: 'Actor'})-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(a2:Person {role: 'Actor'})
                WHERE a1 <> a2
                RETURN a2.name as actor, count(m) as collaboration_count
                ORDER BY collaboration_count DESC
                LIMIT 10
                """
                return session.run(cypher_query, actor_name=params['actor']).data()
            
            return []
    
    def close(self):
        """Close the database connection."""
        self.driver.close() 