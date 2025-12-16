import os

class Config:
    PDF_folder = r"C:\Users\jszuran\Desktop\PDFtoCHUNK"
    MD_folder = r"C:\Users\jszuran\Desktop\PDFtoMarkDownwithPages"
    OUTPUT_folder = r"C:\Users\jszuran\Desktop\chunk_outputs"

    # Milvus
    MILVUS_URI = "http://10.3.9.3:19530"

    # Embedding
    EMBEDDING_SERVER_HOST = "10.3.9.3"
    EMBEDDING_SERVER_PORT = 8000
    EMBEDDING_API_URL = "http://10.3.9.3:8000/v1/embeddings"
    EMBEDDING_MODEL_NAME = "Snowflake/snowflake-arctic-embed-l-v2.0"  #"Snowflake/snowflake-arctic-embed-m-v2.0"
    EMBEDDING_API_KEY = "vLLM"

    # Fixed chunking
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Recursive chunking
    RECURSIVE_CHUNK_SIZE = 1000
    RECURSIVE_CHUNK_OVERLAP = 200

    # Semantic chunking (ilość zdań)
    SEMANTIC_CHUNK_SIZE = 3

    @staticmethod
    def ensure_dirs():
        os.makedirs(Config.OUTPUT_folder, exist_ok=True)

#
#

