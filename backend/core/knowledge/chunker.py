import re
from uuid import uuid4
from core.config import settings


def split_into_sentences(text: str) -> list[str]:
    """
    Lightweight sentence splitter.

    Avoids adding NLTK dependency.
    Splits on:
    - . ! ?
    - paragraph breaks

    Returns clean sentence list.
    """


    if not text:
        return []

    text=text.replace("\r\n","\n")

    sentences= re.split(r"(?<=[.!?])\s+|\n{2,}",text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def chunk_text(
    text: str,
    doc_id: str,
    dept_id: str,
    visibility: str,
    chunk_size: int | None = None,
    overlap: int | None = None
)->list[dict]:
    
    """
    Convert document text into overlapping chunks.

    Strategy:
    - Split into sentences.
    - Build chunks until chunk_size reached.
    - Carry overlap characters into next chunk.
    - Avoid splitting in the middle of sentences.
    """


    chunk_size=chunk_size or settings.CHUNK_SIZE

    overlap= overlap or settings.CHUNK_OVERLAP

    sentences=split_into_sentences(text)

    if not sentences:
        return []

    chunks=[]

    current_chunk=""
    chunk_index=0

    for sentence in sentences:

        candidate=(current_chunk + " " + sentence).strip()

        if len(candidate)<=chunk_size:
            current_chunk=candidate
            continue

        if current_chunk:
            chunks.append(
                {
                    "id": str(uuid4()),
                    "document_id": doc_id,
                    "text": current_chunk,
                    "chunk_index": chunk_index,
                    "department_id": dept_id,
                    "visibility": visibility,
                    "page_number": None
                }
            )

            chunk_index+=1

            overlap_text=(
                current_chunk[-overlap:] if overlap>0 else ""
            )

            current_chunk = (
                overlap_text
                + " "
                + sentence
            ).strip()

        else:
            current_chunk=sentence

    if current_chunk:

        chunks.append(
            {
                "id": str(uuid4()),
                "document_id": doc_id,
                "text": current_chunk,
                "chunk_index": chunk_index,
                "department_id": dept_id,
                "visibility": visibility,
                "page_number": None
            }
        )

    return chunks


