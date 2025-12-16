import os
from chunkers.fixedSize import FixedSizeChunker
from chunkers.recursive import RecursiveChunker
from chunkers.semantic import SemanticChunker
from chunkers.contentAware import ContentAwareChunker
from chunkers.mdsplitter import MarkdownChunker
from readers.pdf_reader import PDFReader
from readers.md_reader import MarkdownReader
from embedder import Embedder
from milvus_connect import MilvusConnector
from utils import save_chunks_to_txt
from config import Config
from gen_question import QuestionGenerator
from chunkToJSON import ChunkToJSON


def main():
    pdf_reader = PDFReader(Config.PDF_folder)
    md_reader = MarkdownReader(Config.MD_folder)
    embedder = Embedder()
    milvus = MilvusConnector()

    chunkers = {
        "fixed_size": FixedSizeChunker(),
        "recursive": RecursiveChunker(),
        "semantic": SemanticChunker(embed_fn=embedder.embed, max_sentences=6, sim_threshold=0.60),
        "content_aware": ContentAwareChunker(), 
        "markdown": MarkdownChunker()
    }
    #print("Klucze w pierwszym chunku:", chunks[0].keys())

    print("=== CHUNKOWANIE DOKUMENTÓW ===")
    print("Wybierz typ dokumentów do przetworzenia:")
    print("1 - PDF")
    print("2 - Markdown (.md)")
    choice = input("Twój wybór: ")

    if choice == "1":
        files = [os.path.join(Config.PDF_folder, f) for f in os.listdir(Config.PDF_folder) if f.endswith(".pdf")]
        reader = pdf_reader
    elif choice == "2":
        files = [os.path.join(Config.MD_folder, f) for f in os.listdir(Config.MD_folder) if f.endswith(".md")]
        reader = md_reader
    else:
        print("Niepoprawny wybór.")
        return

    if not files:
        print("Brak plików w folderze.")
        return

    print("Dostępne pliki:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {os.path.basename(file)}")

    file_indices = input("Podaj numery plików do przetworzenia (oddzielone przecinkami, np. 1,3) lub wybierz wszystkie (wpisz 'all'): ").strip().lower()
   
    selected_files = []
    try:
        if file_indices == "all":
            selected_files = files[:]  # wszystkie pliki
        else:
            for idx in file_indices.split(","):
                selected_files.append(files[int(idx.strip()) - 1])
    except Exception:
        print("Błędne numery plików.")
        return

    print("\nDostępne metody chunkowania:")
    for i, method in enumerate(chunkers.keys(), 1):
        print(f"{i}. {method}")
    method_choice = input("Wybierz metodę: ")

    try:
        method_name = list(chunkers.keys())[int(method_choice) - 1]
    except Exception:
        print("Błędny wybór metody.")
        return

    chunker = chunkers[method_name]

    for filepath in selected_files:
        filename = os.path.basename(filepath)
        try:
            text = reader.read(filepath)
        except Exception as e:
            print(f"Błąd odczytu pliku {filename}: {e}")
            continue
        
        file_path = os.path.join(Config.MD_folder, filename)  # folder np. "PDFtoCHUNK" albo "MDtoCHUNK"
        with open(file_path, "r", encoding="utf-8") as f:
            original_text = f.read()
        chunks = chunker.chunk(text, source_file=filename, method=method_name)
        #embeddings = [[0.0] * 768 for _ in chunks]  # dummy wektor, żeby kod się nie wywalił
        embeddings = embedder.embed([chunk["chunk"] for chunk in chunks])
        milvus.upsert_chunks(method_name, chunks, embeddings)
        json_out = r"C:\Users\jszuran\Desktop\chunk_to_json"
        saver = ChunkToJSON(json_out)
        saver.save(chunks, filename)#, original_text= original_text)
        #saver.save(chunks, filename, original_text_path=path_to_md)
        save_chunks_to_txt(chunks, method_name, filename, Config.OUTPUT_folder)
        qgen = QuestionGenerator()
        all_results = []

        #for ch in chunks[:10]:  # tylko dla pierwszych 10 chunków
        #    result = qgen.generate_questions(ch["text"])
        #    all_results.append(result)
        #
        #    print(result)
        #qgen.save_to_json(all_results, source_file=filename)
if __name__ == "__main__":
    main()
    #