from dataclasses import dataclass
from typing import Dict, Any

from solrcloudpy.collection.data.dtos.dto_utlils import from_str
from solrcloudpy.collection.data.models.field_type_model_dto import FieldTypeModelDto


@dataclass
class FieldModelDto:
    name: str
    field_type_model: FieldTypeModelDto

    @staticmethod
    def from_json(obj: Dict[str, Any]) -> 'FieldModelDto':
        assert isinstance(obj, Dict)
        name = from_str(obj.get("name"))
        field_type_model = FieldTypeModelDto.from_field_model_json(obj=obj)
        return FieldModelDto(name, field_type_model)

    @property
    def is_internal(self) -> bool:
        return self.name.startswith('_')
