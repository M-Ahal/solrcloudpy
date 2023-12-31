from dataclasses import dataclass
from typing import Any, List, Tuple

from solrcloudpy.collection.data.dtos.dto_utlils import from_str, from_bool, from_list, from_int
from solrcloudpy.collection.data.enums.solr_field_type import SolrFieldType


@dataclass
class Field:
    name: str
    type: str
    indexed: bool
    stored: bool
    multi_valued: bool

    @staticmethod
    def from_dict(obj: dict[str, Any]) -> 'Field':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        type = from_str(obj.get("type"))
        indexed = from_bool(obj.get("indexed"))
        stored = from_bool(obj.get("stored"))
        # Mirroring defaults def in
        # https://solr.apache.org/guide/solr/latest/indexing-guide/fields.html#optional-field-type-override-properties
        multi_valued = obj.get("multiValued") or False
        return Field(name, type, indexed, stored, multi_valued)

    def to_json(self) -> dict[str, Any]:
        return {
            "name": from_str(self.name),
            "type": from_str(self.type),
            "indexed": from_bool(self.indexed),
            "stored": from_bool(self.stored),
            "multiValued": from_bool(self.multi_valued)
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        # # Special case for repeatable tags
        # if self.multi_valued and other.multi_valued:
        #     return self.name == other.name and self.type == other.type

        return self.name == other.name and self.type == other.type

    @staticmethod
    def from_field_name_and_data(field_name_and_data: Tuple[str, SolrFieldType]) -> 'Field':
        return Field(
            name=field_name_and_data[0],
            type=str(field_name_and_data[1]),
            indexed=True,
            stored=False,
            multi_valued=False
        )


@dataclass
class _ResponseHeader:
    status: int
    q_time: int

    @staticmethod
    def _from_dict(obj: dict[str, Any]) -> '_ResponseHeader':
        assert isinstance(obj, dict)
        status = from_int(obj.get("status"))
        q_time = from_int(obj.get("QTime"))
        return _ResponseHeader(status, q_time)


@dataclass
class SolrSchemaFieldsInfoDTO:
    response_header: _ResponseHeader
    fields: List[Field]

    @staticmethod
    def from_json(json: dict[str, Any]) -> 'SolrSchemaFieldsInfoDTO':
        assert isinstance(json, dict)
        response_header = _ResponseHeader._from_dict(json.get("responseHeader"))  # type: ignore
        fields = from_list(Field.from_dict, json.get("fields"))
        return SolrSchemaFieldsInfoDTO(response_header, fields)
