from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from config import Config
import uuid
import logging
import time


class MilvusConnector:
    def __init__(self, host="10.3.9.3", port="19530"):
        # Łączenie z Milvus
        try:
            connections.connect(
                alias="default",
                host=host,
                port=port
            )
            print(f"Połączono z Milvus ({host}:{port})")
        except Exception as e:
            print("Błąd połączenia z Milvus:", e)

    def _get_collection_name(self, method):
        # Nazwa kolekcji zależna od metody chunkowania
        return f"zbior_{method}"

    def _create_collection_if_not_exists(self, collection_name, dim):
        # Tworzenie kolekcji jeśli jeszcze nie istnieje
        try:
            if utility.has_collection(collection_name):
                return Collection(name=collection_name)

            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="source_file", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
            ]

            schema = CollectionSchema(
                fields=fields,
                description=f"Kolekcja dokumentów dla metody: {collection_name}"
            )

            collection = Collection(name=collection_name, schema=schema)

            collection.create_index(
                field_name="embedding",
                index_params={
                    "index_type": "IVF_FLAT",
                    "metric_type": "COSINE",
                    "params": {"nlist": 1024}
                }
            )

            print(f"Utworzono nową kolekcję: {collection_name}")
            return collection
        except Exception as e:
            print(f"Błąd przy tworzeniu kolekcji '{collection_name}':", e)
            return None

    def store_chunks(self, method, chunks, embeddings):
        if not chunks or not embeddings:
            print("Brak chunków lub embeddingów do zapisania.")
            return

        collection_name = self._get_collection_name(method)
        dim = len(embeddings[0]) if embeddings else 0

        collection = self._create_collection_if_not_exists(collection_name, dim)
        if not collection:
            return
        collection.load()
    # Walidacja chunków
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            if "metadata" not in chunk or "source_file" not in chunk["metadata"]:
                print(f"Chunk nr {i} nie ma klucza 'metadata' lub 'source_file': {chunk}")
                continue
            if "text" not in chunk:
                print(f"Chunk nr {i} nie ma klucza 'text': {chunk}")
                continue
            valid_chunks.append(chunk)

            if not valid_chunks:
                print("Brak poprawnych chunków do zapisania.")
                return

        source_files = [chunk["metadata"]["source_file"] for chunk in valid_chunks]
        texts = [chunk["text"] for chunk in valid_chunks]
        valid_embeddings = embeddings[:len(valid_chunks)]

        try:
            collection.insert([source_files, texts, valid_embeddings])
            collection.flush()
            print(f"Zapisano {len(valid_chunks)} chunków do kolekcji '{collection_name}'.")
        except Exception as e:
            print("Błąd przy zapisie chunków:", e)
    
    def replace_document_chunks(self, method, source_file, chunks, embeddings):
        
        #Usuwa istniejące chunki dokumentu i zastępuje je nowymi.
        #
        #Args:
        #    method (str): metoda chunkowania (np. "semantic")
        #    source_file (str): nazwa pliku źródłowego
        #    chunks (list): lista nowych chunków [{"text": ..., "metadata": {...}}]
        #    embeddings (list): embeddingi dla chunków
        
        collection_name = self._get_collection_name(method)
        dim = len(embeddings[0]) if embeddings else 0

        collection = self._create_collection_if_not_exists(collection_name, dim)
        if not collection:
            return

        try:
            # 1. Usunięcie starych chunków
            existing = collection.query(
                expr=f'source_file == "{source_file}"',
                output_fields=["source_file"]
            )
            if existing:
                print(f"Dokument '{source_file}' istnieje ({len(existing)} chunków). Usuwam stare...")
                collection.delete(expr=f'source_file == "{source_file}"')

            # 2. Walidacja i zapis nowych chunków
            valid_chunks = []
            for i, chunk in enumerate(chunks):
                if "metadata" not in chunk or "source_file" not in chunk["metadata"]:
                    print(f"Chunk nr {i} nie ma klucza 'metadata' lub 'source_file': {chunk}")
                    continue
                if "text" not in chunk:
                    print(f"Chunk nr {i} nie ma klucza 'text': {chunk}")
                    continue
                valid_chunks.append(chunk)

            if not valid_chunks:
                print("Brak poprawnych chunków do zapisania.")
                return

            source_files = [chunk["metadata"]["source_file"] for chunk in valid_chunks]
            texts = [chunk["text"] for chunk in valid_chunks]
            valid_embeddings = embeddings[:len(valid_chunks)]

            collection.insert([source_files, texts, valid_embeddings])
            collection.flush()

            print(f"Dokument '{source_file}' został zaktualizowany ({len(valid_chunks)} chunków).")

        except Exception as e:
            print(f"Błąd przy aktualizacji dokumentu '{source_file}': {e}")

    def upsert_chunks(self, method, chunks, embeddings):
        
        #Usuwa stare chunki dla każdego source_file występującego w 'chunks' i wstawia nowe
        
        if not chunks or not embeddings:
            print("Brak chunków lub embeddingów do zapisania.")
            return

        collection_name = self._get_collection_name(method)
        dim = len(embeddings[0]) if embeddings else 0
        collection = self._create_collection_if_not_exists(collection_name, dim)
        if not collection:
            return

        try:
            collection.load()
        except Exception as e:
            print(f"Ostrzeżenie: nie udało się załadować kolekcji {collection_name}: {e}")
        
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            if "metadata" not in chunk or "source_file" not in chunk["metadata"]:
                print(f"Chunk nr {i} nie ma klucza 'metadata' lub 'source_file': {chunk}")
                continue
            if "text" not in chunk:
                print(f"Chunk nr {i} nie ma klucza 'text': {chunk}")
                continue
            valid_chunks.append(chunk)

        if not valid_chunks:
            print("Brak poprawnych chunków do zapisania.")
            return

        # Zbierz unikalne pliki, które będziemy podmieniać
        unique_files = sorted(set(ch["metadata"]["source_file"] for ch in valid_chunks))

        # (Opcjonalnie) upewnij się, że indeks jest zbudowany – jeśli to świeża kolekcja
        try:
            utility.wait_for_index_building_complete(collection.name)
        except Exception as e:
            # nie krytyczne – tylko ostrzeżenie
            logging.debug(f"wait_for_index_building_complete: {e}")

        # Skasuj stare chunki dla każdego pliku
        for sf in unique_files:
            # zabezpieczenie na cudzysłowy w ścieżce
            sf_escaped = sf.replace('"', r'\"')
            try:
                collection.delete(expr=f'source_file == "{sf_escaped}"')
            except Exception as e:
                print(f"Ostrzeżenie: problem z delete dla {sf}: {e}")

        collection.flush()

        # Przygotuj dane do inserta
        source_files = [ch["metadata"]["source_file"] for ch in valid_chunks]
        texts = [ch["text"] for ch in valid_chunks]
        valid_embeddings = embeddings[:len(valid_chunks)]

        try:
            collection.insert([source_files, texts, valid_embeddings])
            collection.flush()
            print(f"Zapisano {len(valid_chunks)} chunków do kolekcji '{collection_name}' (upsert).")
        except Exception as e:
            print("Błąd przy zapisie chunków:", e)
