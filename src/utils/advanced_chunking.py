from langchain_community.document_loaders import markdown
from langchain.text_splitter import MarkdownHeaderTextSplitter

def chunk_markdown_by_header(markdown_text: str) -> list:
    """Chunks markdown text based on headers H1-H4.

    Args:
        markdown_text: The markdown text to chunk.

    Returns:
        A list of dictionaries, where each dictionary represents a chunk and contains the content and metadata.
    """
    headers_to_split_on = [
        ("H1", "# "),
        ("H2", "## "),
        ("H3", "### "),
        ("H4", "#### "),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    chunks = markdown_splitter.split_text(markdown_text)
    return chunks
