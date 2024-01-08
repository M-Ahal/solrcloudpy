from dataclasses import dataclass
from typing import Dict, Any

from solrcloudpy.collection.data.models.dto_utlils import from_str
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

    def to_add_field_json(self) -> Dict[str, Dict[str, Any]]:
        nested_dto = self.field_type_model.to_add_field_type_json()['add-field-type']
        # Rename ['name'] with ['type']
        nested_dto['type'] = nested_dto.pop('name')

        combined_dto: Dict[str, Dict[str, Any]] = {
            'add-field': {
                'name': self.name
            }
        }
        combined_dto['add-field'].update(nested_dto)
        return combined_dto

    def to_delete_field_json(self) -> Dict[str, Dict[str, Any]]:
        return {
            'delete-field': {
                'name': self.name
            }
        }

    @property
    def is_internal(self) -> bool:
        return self.name.startswith('_')
