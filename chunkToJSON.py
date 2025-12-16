"""import re
import json
from pathlib import Path

class ChunkToJSON:
    def __init__(self, json_out_dir):
        self.json_out_dir = Path(json_out_dir)
        self.json_out_dir.mkdir(parents=True, exist_ok=True)

    def _clean_markers(self, text: str) -> str:
        #Usuwa markery <!-- Strona X --> z tekstu.
        return re.sub(r"<!--\s*Strona\s+\d+\s*-->", "", text)

    def _assign_pages_simple(self, chunks, page_ranges):
        
        #Przypisuje stronę chunkowi na podstawie startowego znaku (po markerach usuniętych).
        
        json_chunks = []
        char_count = 0  # globalny offset w clean_text

        for c in chunks:
            clean_text = self._clean_markers(c.get("chunk", ""))
            start_char = char_count
            end_char = start_char + len(clean_text)
            char_count = end_char  # przesuwamy offset globalny

            page_num = None
            for start, end, pnum in page_ranges:
                if start <= start_char < end:
                    page_num = pnum
                    break

            json_chunks.append({
                "chunk": clean_text.strip(),
                "numer strony": page_num,
                "starting character": start_char,
                "position": None  # tu możemy ewentualnie policzyć % pozycji na stronie
            })

        return json_chunks

    def save(self, chunks, source_file: str, page_ranges=None):
        
        #Zapisuje chunki w formacie JSON z numerami stron.
        #page_ranges – lista [(start, end, page_num), ...]
        
        base_name = Path(source_file).stem

        if page_ranges is not None:
            json_chunks = self._assign_pages_simple(chunks, page_ranges)
        else:
            # fallback jeśli brak page_ranges
            json_chunks = [{
                "chunk": self._clean_markers(c.get("chunk", "")),
                "numer strony": None,
                "starting character": None,
                "position": None
            } for c in chunks]

        json_path = self.json_out_dir / f"{base_name}_chunks.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_chunks, f, ensure_ascii=False, indent=4)

        print(f"Zapisano JSON dla {source_file}: {len(chunks)} chunków")"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any


class ChunkToJSON:
    
    #Klasa do zapisywania chunków do formatu JSON z informacjami o stronach.
    
    
    def __init__(self, output_dir: str):
        """
        Args:
            output_dir: Folder docelowy dla plików JSON
        """
        self.output_dir = Path(r"C:\Users\jszuran\Desktop\chunk_to_json")
        #self.output_dir.mkdir(exist_ok=True)
    
    def save(self, chunks: List[Dict[str, Any]], source_filename: str) -> str:
        """
        Zapisuje chunki do pliku JSON z pełnymi informacjami o pozycji na stronie.
        
        Args:
            chunks: Lista chunków z metadanymi (zawierającymi informacje o stronie)
            source_filename: Nazwa oryginalnego pliku (np. "dokument.md")
            
        Returns:
            str: Ścieżka do zapisanego pliku JSON
        """
        # Przygotuj dane do zapisu
        chunks_data = []
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            
            chunk_json = {
                "chunk": chunk.get("chunk", chunk.get("text", "")),
                "numer_strony": metadata.get("page_number", 1),
                "starting_character": metadata.get("starting_char", 0),
                "ending_character": metadata.get("ending_char", 0),
                "position": metadata.get("position", 0.0)
            }
            
            chunks_data.append(chunk_json)
        
        # Przygotuj nazwę pliku wyjściowego
        base_name = Path(source_filename).stem
        output_filename = f"{base_name}_chunks.json"
        output_path = self.output_dir / output_filename
        
        # Zapisz do JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        print(f"Zapisano {len(chunks_data)} chunków z pełnymi informacjami o pozycji do: {output_path}")
        return str(output_path)
    
    def save_with_metadata(self, chunks: List[Dict[str, Any]], source_filename: str) -> str:
        """
        Alternatywna metoda - zapisuje chunki z pełnymi metadanymi.
        
        Args:
            chunks: Lista chunków z metadanymi
            source_filename: Nazwa oryginalnego pliku
            
        Returns:
            str: Ścieżka do zapisanego pliku JSON
        """
        chunks_data = []
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            
            chunk_json = {
                "chunk": chunk.get("chunk", chunk.get("text", "")),
                "numer_strony": metadata.get("page_number", 1),
                "chunk_id": metadata.get("chunk_id", 0),
                "source_file": metadata.get("source_file", source_filename),
                "method": metadata.get("method", "unknown")
            }
            
            chunks_data.append(chunk_json)
        
        # Przygotuj nazwę pliku wyjściowego
        base_name = Path(source_filename).stem
        output_filename = f"{base_name}_chunks_full.json"
        output_path = self.output_dir / output_filename
        
        # Zapisz do JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        print(f"Zapisano {len(chunks_data)} chunków z metadanymi do: {output_path}")
        return str(output_path)