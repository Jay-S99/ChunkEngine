import os

def save_chunks_to_txt(chunks, method, filename, output_dir):
    try:
        name, ext = os.path.splitext(filename)
        ext = ext.replace('.', '')  # usuwa kropkę z rozszerzenia

        output_folder = os.path.join(output_dir, method)
        os.makedirs(output_folder, exist_ok=True)

        output_path = os.path.join(output_folder, f"{name}_{ext}_chunks.txt")

        with open(output_path, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(chunks):
                f.write(f"--- Chunk {i+1} ---\n")
                f.write(chunk["text"] + "\n\n")

        print(f"Zapisano {len(chunks)} chunków do pliku: {output_path}")
    except Exception as e:
        print(f"Błąd podczas zapisu chunków do pliku: {e}")
