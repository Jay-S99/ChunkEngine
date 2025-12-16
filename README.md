# ChunkEngine
It's a project I made during my Internship. A Python-based document chunking tool for RAG pipelines, utilizing LangChain for segmentation and Milvus for vector storage.

This project implements an efficient data preprocessing pipeline designed for Retrieval-Augmented Generation (RAG) systems. Built with Python and LangChain, it handles document ingestion and intelligent chunking strategies to optimize context retrieval. The processed data is prepared for high-performance vector storage in Milvus.
## 🚀 Features

This application streamlines the data ingestion process for RAG systems by providing a flexible pipeline for document processing.

* **Multi-Format Support**: Seamlessly ingests and processes raw data from **PDF** and **Markdown** files.
* **Diverse Chunking Strategies**: Implements a variety of LangChain-based splitting methods to optimize semantic retrieval:
    * **Recursive**: Maintains context by splitting on separators recursively.
    * **MarkdownHeader**: Respects document structure by splitting based on headers (`#`, `##`).
    * **Semantic**: Groups text based on meaning rather than just character count.
    * **Content-Aware**: Adapts splitting logic to the specific content type.
    * **Fixed Size**: Standard chunks for consistent embedding dimensions.
* **Vector Integration**: Automatically formats processed chunks for insertion into the **Milvus** vector database.
