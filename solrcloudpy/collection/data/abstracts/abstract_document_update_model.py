from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List

from solrcloudpy.collection.data.abstracts.abstract_document_model import AbstractDocumentModel


@dataclass
class AbstractDocumentUpdateModel(ABC):
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
