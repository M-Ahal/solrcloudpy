import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List

from solrcloudpy.collection.data.abstracts.abstract_document_model import AbstractDocumentModel


@dataclass
class AbstractDocumentUpdateModelDto(ABC):
    # TODO(mehul): Check tradeoff between reads, for using Iterable instead
    documents_update_batch: List[AbstractDocumentModel] = field()

    @abstractmethod
    def __init__(self, *args: Any) -> None:
        pass

    def to_json(self) -> List[Dict[str, Any]]:
        return [
            document_update_model.to_json()
            for document_update_model in self.documents_update_batch
        ]

    def to_bytes(self) -> bytes:
        return pickle.dumps(obj=self, protocol=pickle.HIGHEST_PROTOCOL)

    def __len__(self) -> int:
        return len(self.documents_update_batch)

    def __str__(self) -> str:
        return f"DocumentUpdateModel(solr_products={self.documents_update_batch})"

    def __repr__(self) -> str:
        return f"DocumentUpdateModel(solr_products={self.documents_update_batch})"