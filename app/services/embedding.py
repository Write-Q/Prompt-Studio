"""文本向量化(embedding)：把文本转成向量，用于语义检索。

- 用 sentence-transformers + BGE 中文模型，本地运行。
- 模型懒加载：第一次用时才下载 / 载入(避免一启动就吃 torch)。
- 归一化向量(unit vector)：此时「余弦相似度 = 点积」，算起来最省。
- 通用：卡片、模板都用同一套 embed / 排序。
"""

import json
from functools import lru_cache

MODEL_NAME = "BAAI/bge-small-zh-v1.5"  # 512 维，中文检索友好，体积小
# BGE 检索建议给「查询」加指令前缀(对短查询提升召回)；文档/卡片正文不加。
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："
SIMILARITY_THRESHOLD = 0.35  # 余弦低于此值视为不相关，宁缺毋滥(卡片/模板共用，可调)


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer  # 延迟导入

    return SentenceTransformer(MODEL_NAME)


def embed(text: str, is_query: bool = False) -> list[float]:
    """把一段文本转成归一化向量。查询用 is_query=True(会加指令前缀)。"""
    payload = (QUERY_INSTRUCTION + text) if is_query else text
    vector = _get_model().encode(payload, normalize_embeddings=True)
    return [float(x) for x in vector]


def embed_documents(texts: list[str]) -> list[list[float]]:
    """批量给文档/卡片正文做 embedding(不加查询前缀)。"""
    if not texts:
        return []
    vectors = _get_model().encode(texts, normalize_embeddings=True)
    return [[float(x) for x in v] for v in vectors]


def cosine(a: list[float], b: list[float]) -> float:
    """已归一化向量的余弦相似度 = 点积。"""
    return sum(x * y for x, y in zip(a, b))


def top_k_by_cosine(query_vec, candidates, k, min_score=0.0):
    """candidates: [(item, vector), ...]，返回相似度 >= min_score 中最高的前 k 个 item。"""
    scored = [(cosine(query_vec, vec), item) for item, vec in candidates]
    scored = [pair for pair in scored if pair[0] >= min_score]
    scored.sort(key=lambda pair: -pair[0])
    return [item for _, item in scored[:k]]


def serialize_vector(vector: list[float]) -> str:
    return json.dumps(vector)


def deserialize_vector(text: str | None) -> list[float] | None:
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, list) else None
