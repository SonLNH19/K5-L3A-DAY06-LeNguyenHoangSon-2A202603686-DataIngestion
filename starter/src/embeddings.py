"""Real local embedding model shared by documents and queries."""
from pathlib import Path

from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

MODEL_NAME = 'all-MiniLM-L6-v2'
MODEL_HASH = '913d7300ceae3b2dbc2c50d1de4baacab4be7b9380491c27fab7418616a16ec3'
DIMENSIONS = 384


def embedder():
    """Load Chroma's ONNX implementation; first use downloads the verified model."""
    model = ONNXMiniLM_L6_V2()
    model.DOWNLOAD_PATH = Path(__file__).resolve().parents[1] / '.models' / MODEL_NAME
    return model
