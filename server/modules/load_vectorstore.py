import os
import time
from pathlib import Path

from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

PINECONE_REGION = "us-east-1"
PINECONE_INDEX_NAME = "medicalindex"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

UPLOAD_DIR = "./uploaded_docs"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

spec = ServerlessSpec(
    cloud="aws",
    region=PINECONE_REGION
)

existing_indexes = [
    index.name
    for index in pc.list_indexes()
]

if PINECONE_INDEX_NAME not in existing_indexes:

    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,
        metric="dotproduct",
        spec=spec
    )

    while not pc.describe_index(
        PINECONE_INDEX_NAME
    ).status["ready"]:

        time.sleep(1)

index = pc.Index(PINECONE_INDEX_NAME)


# Load, split, embed and upload PDFs
def load_vectorstore(uploaded_files):

    embed_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    file_paths = []

    for file in uploaded_files:

        save_path = Path(UPLOAD_DIR) / file.filename

        with open(save_path, "wb") as f:

            f.write(file.file.read())

        file_paths.append(str(save_path))

    for file_path in file_paths:

        # Load PDF
        loader = PyPDFLoader(file_path)

        documents = loader.load()

        # Split text
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(documents)

        # Extract text
        texts = [
            chunk.page_content
            for chunk in chunks
        ]

        # Store text in metadata
        metadatas = [
            {
                "text": chunk.page_content,
                **chunk.metadata
            }
            for chunk in chunks
        ]

        # Create IDs
        ids = [
            f"{Path(file_path).stem}-{i}"
            for i in range(len(chunks))
        ]

        print(f"Embedding {len(texts)} chunks...")

        # Create embeddings
        embeddings = embed_model.embed_documents(texts)

        # Prepare vectors
        vectors = list(
            zip(ids, embeddings, metadatas)
        )

        print("Uploading to Pinecone...")

        # Upload to Pinecone
        index.upsert(vectors=vectors)

        print(f"Upload complete for {file_path}")