from dataclasses import dataclass
from typing import Dict, Any

from solrcloudpy.collection.data.models.dto_utlils import from_str, from_bool
from solrcloudpy.collection.data.enums.field_type_class import FieldTypeClass


@dataclass
class FieldTypeModelDto:
    name: FieldTypeClass
    # TODO(mehul): create (string: solr.String) enum when needing add-field-type api call
    # type_class: str
    indexed: bool
    stored: bool
    doc_values: bool
    multi_valued: bool

    @staticmethod
    def from_json(obj: Dict[str, Any]) -> 'FieldTypeModelDto':
        assert isinstance(obj, Dict)
        name = FieldTypeClass(from_str(obj.get("name")))
        # type_class = from_str(obj.get("class") or 'ignored')
        # Mirroring defaults def in
        # https://solr.apache.org/guide/solr/latest/indexing-guide/fields.html#optional-field-type-override-properties
        indexed = from_bool(obj.get("indexed") or True)
        doc_values = from_bool(obj.get("docValues") or True)
        stored = from_bool(obj.get("stored") or True)
        multi_valued = from_bool(obj.get("multiValued") or False)
        return FieldTypeModelDto(name, indexed, stored, doc_values, multi_valued)

    @staticmethod
    def from_field_model_json(obj: Dict[str, Any]) -> 'FieldTypeModelDto':
        assert isinstance(obj, Dict)
        # Rename ['type'] with ['name']
        obj['name'] = obj.pop('type')
        return FieldTypeModelDto.from_json(obj)

    def to_add_field_type_json(self) -> Dict[str, Dict[str, Any]]:
        add_field_type_dto: Dict[str, Dict[str, Any]] = {
            'add-field-type': {
                'name': str(self.name),
                # 'class': self.solr_class,
                'indexed': self.indexed,
                'stored': self.stored,
                'docValues': self.doc_values,
                'multiValued': self.multi_valued
            }
        }

        non_null_fields = {k: v for k, v in add_field_type_dto['add-field-type'].items() if v is not None}
        add_field_type_dto['add-field-type'].clear()
        add_field_type_dto['add-field-type'].update(non_null_fields)
        return add_field_type_dto

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        # # Special case for repeatable tags
        # if self.multi_valued and other.multi_valued:
        #     return self.name == other.name and self.type == other.type

        return self.name == other.name and self.name == other.name
