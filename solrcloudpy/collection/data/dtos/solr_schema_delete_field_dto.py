from typing import Any

from solrcloudpy.collection.data.dtos.dto_utlils import from_str, to_class


class _DeleteField:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def to_json(self) -> dict[str, Any]:
        return {"name": from_str(self.name)}


class SolrSchemaDeleteFieldDTO:
    delete_field: _DeleteField

    def __init__(self, field_name: str) -> None:
        self.delete_field = _DeleteField(name=field_name)

    def to_json(self) -> dict:
        return {"delete-field": to_class(_DeleteField, self.delete_field)}
