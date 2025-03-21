from setuptools import setup, find_packages

setup(
    name="movie_search_engine",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "neo4j",
        "faiss-cpu",
        "sentence-transformers",
        "tqdm",
    ],
) 