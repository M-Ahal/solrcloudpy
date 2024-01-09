"""
Get and modify schema
"""
import json
from collections import ChainMap
from collections.abc import Iterable, MutableMapping
from http import HTTPStatus
from typing import Any, Optional, Dict, List, Final

from requests import HTTPError

from solrcloudpy.collection.data.enums.field_type_class import FieldTypeClass
from solrcloudpy.collection.data.models.field_model_dto import FieldModelDto
from solrcloudpy.collection.data.models.field_type_model_dto import FieldTypeModelDto
from solrcloudpy.utils import _Request, logger, SolrException


class SolrSchema(object):
    """
    Get and modify schema.
    Uses the Schema API described in https://cwiki.apache.org/confluence/display/solr/Schema+API
    """

    def __init__(self, connection, collection_name: str) -> None:  # type: ignore
        """
        :param connection: the connection to solr
        :type connection: SolrConnection
        :param collection_name: the name of the collection related to the schema
        :type collection_name: str
        """
        self.connection = connection
        self.collection_name = collection_name
        self.client = _Request(connection)

    @property
    async def schema(self) -> Dict[str, Any]:
        """
        Retrieves the schema as a dict
        :return: the schema dict
        :rtype: Dict[str, Any]
        """
        return dict[str, Any](
            self.client.get("%s/schema" % self.collection_name).result.dict['schema'],
            asynchronous=True
        )

    @property
    async def name(self) -> str:
        """
        Retrieves the schema name as a str
        :return: the schema name as a str
        :rtype: str
        """
        return str(
            self.client.get("%s/schema/name" % self.collection_name).result.dict['name']
        )

    @property
    async def version(self) -> str:
        """
        Retrieves the schema version as a dict
        :return: the schema version as a str
        :rtype: str
        """
        return str(self.client.get("%s/schema/version" % self.collection_name).result.dict['version'])

    @property
    async def unique_key(self) -> Optional[str]:
        """
        Retrieves the schema's defined unique key as a dict
        :return: the schema unique key as a dict
        :rtype: dict
        """
        try:
            return str(
                self.client.get(
                    "%s/schema/uniquekey" % self.collection_name
                ).result.dict['unique_key']
            )
        except SolrException:
            logger.warning('Could be due to not having a defined value. Returning None')

    @property
    async def similarity(self) -> str:
        """
        Retrieves the schema's global similarity definition as a str
        :return: the schema global similarity definition as a str
        :rtype: str
        """
        return str(
            self.client.get("%s/schema/similarity" % self.collection_name)
            .result.dict['similarity']['class']
        )

    @property
    async def default_operator(self) -> Optional[str]:
        """
        Retrieves the schema's default operator as a str or None
        :return: the schema default operator as a str or None
        :rtype: Optional[str]
        """
        try:
            return str(
                self.client.get("%s/schema/solrqueryparser/defaultoperator" % self.collection_name)
                .result.dict['default_operator'])
        except HTTPError as ex:
            if ex.response.status_code == HTTPStatus.NOT_FOUND:
                logger.warning('Could be due to not having a defined value. Returning None')
                return None
            raise ex

    # Doesn't work at all <- No endpoint
    # def get_field(self, field):
    #     """
    #     Get information about a field in the schema
    #     TODO: looks like this API will change in newer versions of solr
    #
    #     :param field: the name of the field
    #     :type field: str
    #     :return: a dict related to the field definition
    #     :rtype: dict
    #     """
    #     return self.client.get(
    #         "%s/schema/field/%s" % (self.collection_name, field)
    #     ).result.dict

    async def get_fields(self) -> List[FieldModelDto]:
        """
        Get information about all field in the schema

        :return: a dict of fields to their schema definitions
        :rtype: dict
        """
        return [
            FieldModelDto.from_json(solr_field) for solr_field in
            self.client.get("%s/schema/fields" % self.collection_name).result.dict['fields']
        ]

    async def add_fields(self, field_model_dtos: Iterable[FieldModelDto]) -> bool:
        """
        Add fields to the schema
        :param field_model_dtos: specs for the fields to add
        :type field_model_dtos: Iterable[FieldModelDto]
        :return: a success/failure result of the update request
        :rtype: bool
        """
        add_field_mappings: Iterable[MutableMapping] = ChainMap(
            *map(lambda dto: dto.to_add_field_json(), field_model_dtos)
        ).maps
        # Need to work in string-domain as adding dicts with the same key overwrites it
        # noinspection DuplicatedCode
        serialized_jsons: Final = ','.join([
            json.dumps(add_field_mapping)[1:-1]
            for add_field_mapping in add_field_mappings
        ])

        try:
            self.client.update("%s/schema/fields" % self.collection_name, body="{{{}}}".format(serialized_jsons))

            return True
        except HTTPError as http_error:
            if http_error.response.status_code == HTTPStatus.BAD_REQUEST:
                return False
            raise http_error

    # noinspection DuplicatedCode
    async def delete_fields(self, field_model_dtos: Iterable[FieldModelDto]) -> bool:
        delete_field_mappings: Iterable[MutableMapping] = ChainMap(
            *map(lambda dto: dto.to_delete_field_json(), field_model_dtos)
        ).maps
        # Need to work in string-domain as adding dicts with the same key overwrites it
        # noinspection DuplicatedCode
        serialized_jsons: Final = ','.join([
            json.dumps(delete_field_mapping)[1:-1]
            for delete_field_mapping in delete_field_mappings
        ])

        try:
            self.client.update("%s/schema/fields" % self.collection_name, body="{{{}}}".format(serialized_jsons))
            return True
        except HTTPError as http_error:
            if http_error.response.status_code == HTTPStatus.BAD_REQUEST:
                return False
            raise http_error

    def get_dynamic_fields(self) -> Dict[str, Any]:
        """
        Get information about a dynamic field in the schema
        :return: a dict of dynamic fields to their schema definitions
        :rtype: dict
        """
        return self.client.get(
            "%s/schema/dynamicfields" % self.collection_name
        ).result.dict

    def get_dynamic_field(self, field) -> Dict[str, Any]:
        """
        Get information about a dynamic field in the schema
        TODO: this will change in later version of solr

        :param field: the name of the field
        :type field: str
        :return: a dict of dynamic fields to their schema definitions
        :rtype: dict
        """
        return self.client.get(
            "%s/schema/dynamicfield/%s" % (self.collection_name, field)
        ).result.dict

    async def get_field_types(self) -> List[FieldTypeModelDto]:
        """
        Get information about field types in the schema
        :return: a dict relating information about field types
        :rtype: dict
        """
        return [
            FieldTypeModelDto.from_json(field_type)
            for field_type in self.client.get("%s/schema/fieldtypes" % self.collection_name)
            .result.dict['fieldTypes']
        ]

    async def get_field_type(self, solr_field_type: FieldTypeClass) -> FieldTypeModelDto:
        """
        Get information about a field type in the schema

        :param solr_field_type: the name of the field type
        :type solr_field_type: str
        :return: a dict relating information about a given field type
        :rtype: dict
        """
        return FieldTypeModelDto.from_json(self.client.get(
            "%s/schema/fieldtypes/%s" % (self.collection_name, str(solr_field_type))
        ).result.dict['fieldType'])

    def get_copyfields(self) -> Dict[str, Any]:
        """
        Get information about all copy field in the schema
        :return: a dict describing the copyfields defined in the schema
        :rtype: dict
        """
        return self.client.get(
            "%s/schema/copyfields" % self.collection_name
        ).result.dict

    def get_copyfield(self, field: str) -> Dict[str, Any]:
        """
        Get information about a copy field in the schema

        :param field: the name of the field type
        :type field: str
        :return: a dict relating information about a given copyfield
        :rtype: dict
        """
        return self.client.get(
            "%s/schema/copyfield/%s" % (self.collection_name, field)
        ).result.dict

    def add_synonym(self, syn_data: dict, language: str = "english") -> Dict[str, Any]:
        """
        Adds synonym into collection

        :param syn_data: weighted synonym data {"error":["alert|1.0"]}
        :type syn_data: dict
        :param language: synonym language
        :type language: str
        :return: a dict relating information about added synonym
        :rtype: dict
        """
        synonyms = json.dumps(syn_data)
        return self.client.put(
            "%s/schema/analysis/synonyms/%s" % (self.collection_name, language),
            body=synonyms,
        ).result.dict

    def delete_synonym(self, synonym: str, language: str = "english") -> Dict[str, Any]:
        """
        Deleted synonym into collection

        :param synonym: name of synonym to delete
        :type synonym: str
        :param language: synonym's language
        :type language: str
        :return: a dict relating information about added synonym
        :rtype: dict
        """
        return self.client.delete(
            "%s/schema/analysis/synonyms/%s/%s"
            % (self.collection_name, language, synonym)
        ).result.dict
