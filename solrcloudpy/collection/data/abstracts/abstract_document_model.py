import dataclasses
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Generic, Optional, TypeVar

from solrcloudpy.collection.data.enums.field_type_class import FieldTypeClass

T = TypeVar('T')

@dataclasses.dataclass
class PythonToSolrTypeBinding(Generic[T]):
    solr_type: FieldTypeClass = dataclasses.field()
    value: Optional[T] = dataclasses.field(default=None)

class AbstractDocumentModel(ABC):
    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def get_solr_field_names_and_types(cls) -> List[Tuple[str, FieldTypeClass]]:
        pass
