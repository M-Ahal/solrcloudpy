from dataclasses import dataclass
from typing import Any

from solrcloudpy.collection.data.dtos.dto_utlils import to_class
from solrcloudpy.collection.data.models.field_type_model_dto import Field


@dataclass
class SolrSchemaAddFieldDTO:
    add_field: Field

    def to_json(self) -> dict[str, Any]:
        return {
            "add-field": to_class(Field, self.add_field)
        }


def solr_schema_add_field_to_dict(x: SolrSchemaAddFieldDTO) -> Any:
    return to_class(SolrSchemaAddFieldDTO, x)
