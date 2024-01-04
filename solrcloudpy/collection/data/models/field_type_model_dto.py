from dataclasses import dataclass
from typing import Dict, Any

from solrcloudpy.collection.data.dtos.dto_utlils import from_str, from_bool
from solrcloudpy.collection.data.enums.field_type_class import FieldTypeClass


@dataclass
class FieldTypeModelDto:
    name: FieldTypeClass
    type_class: str
    indexed: bool
    stored: bool
    doc_values: bool
    multi_valued: bool

    @staticmethod
    def from_json(obj: Dict[str, Any]) -> 'FieldTypeModelDto':
        assert isinstance(obj, Dict)
        name = FieldTypeClass(from_str(obj.get("name")))
        # TODO(mehul): create (string: solr.String) mapping or fetch from api
        type_class = from_str(obj.get("class") or 'ignored')
        # Mirroring defaults def in
        # https://solr.apache.org/guide/solr/latest/indexing-guide/fields.html#optional-field-type-override-properties
        indexed = from_bool(obj.get("indexed") or True)
        doc_values = from_bool(obj.get("docValues") or True)
        stored = from_bool(obj.get("stored") or True)
        multi_valued = from_bool(obj.get("multiValued") or False)
        return FieldTypeModelDto(name, type_class, indexed, stored, doc_values, multi_valued)

    @staticmethod
    def from_field_model_json(obj: Dict[str, Any]) -> 'FieldTypeModelDto':
        assert isinstance(obj, Dict)
        # Delete the redundant ['name'] entry
        # del obj['name']
        # Rename ['type'] with ['name']
        obj['name'] = obj.pop('type')
        return FieldTypeModelDto.from_json(obj)

    # def to_json(self) -> dict[str, Any]:
    #     return {
    #         "name": from_str(self.type_name),
    #         "class": from_str(self.solr_class),
    #         "indexed": from_bool(self.indexed),
    #         "stored": from_bool(self.stored),
    #         "docValues": from_bool(self.doc_values),
    #         "multiValued": from_bool(self.multi_valued)
    #     }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        # # Special case for repeatable tags
        # if self.multi_valued and other.multi_valued:
        #     return self.name == other.name and self.type == other.type

        return self.name == other.name and self.type_class == other.type_class
