"""
Manage and administer a collection
"""
import logging
import time
import uuid
from typing import Any, Union

import requests

from solrcloudpy.utils import CollectionBase, SolrException, SolrResponse, AsyncResponse

from .schema import SolrSchema
from .stats import SolrIndexStats


class SolrCollectionAdmin(CollectionBase):
    """
    Manage and administer a collection
    """

    def __init__(self, connection, name: str) -> None:  # type: ignore
        """
        :param connection: the connection to Solr
        :type connection: SolrConnection
        :param name: the name of the collection
        :type name: str
        """
        super(SolrCollectionAdmin, self).__init__(connection, name)

        # corresponding public methods are memoized for a lower memory footprint
        self._index_stats = None
        self._schema = None

    def exists(self) -> bool:
        """
        Finds if a collection exists in the cluster
        :return: whether a collection exists in the cluster
        :rtype: bool
        """
        return self.name in self.connection.list()

    def get_params(self, **kwargs) -> dict[str, Any]:
        params = {
            "name": self.name,
            "replicationFactor": kwargs.get("replication_factor", 1),
            "router.name": kwargs.get("router_name", "compositeId"),
            "numShards": kwargs.get("num_shards", "1"),
            "maxShardsPerNode": kwargs.get("max_shards_per_node", 1),
        }

        shards = kwargs.get("shards")
        if shards:
            params["shards"] = shards

        create_node_set = kwargs.get("create_node_set")
        if create_node_set:
            params["createNodeSet"] = create_node_set

        collection_config_name = kwargs.get("collection_config_name")
        if collection_config_name:
            params["collection.configName"] = collection_config_name

        router_field = kwargs.get("router_field")
        if router_field:
            params["router.field"] = router_field

        tlog_replicas = kwargs.get("tlog_replicas")
        if tlog_replicas:
            params["tlog_replicas"] = tlog_replicas

        pull_replicas = kwargs.get("pull_replicas")
        if pull_replicas:
            params["pull_replicas"] = pull_replicas

        nrt_replicas = kwargs.get("nrt_replicas")
        if nrt_replicas:
            params["nrt_replicas"] = nrt_replicas

        auto_add_replicas = kwargs.get("auto_add_replicas")
        if auto_add_replicas:
            params["auto_add_replicas"] = auto_add_replicas

        return params

    def create(self, force: bool = False, **kwargs):  # type: ignore
        """
        Create a collection

        :param force: a boolean value indicating whether to force the operation
        :type force: bool

        :param kwargs: additional parameters to be passed to this operation
        :Additional Parameters:
            - `replication_factor`: an integer indicating the number of replicas for this collection
            - `router_name`: router name that will be used. defines how documents will be distributed among the shards
            - `num_shards`: number of shards to create for this collection
            - `shards`: A comma separated list of shard names. Required when using the `implicit` router
            - `max_shards_per_node`: max number of shards/replicas to put on a node for this collection
            - `create_node_set`: Allows defining which nodes to spread the new collection across.
            - `collection_config_name`: the name of the configuration to use for this collection
            - `router_field`: if this field is specified, the router will look at the value of the field in an input
                document to compute the hash and identify of a shard instead of looking at the `uniqueKey` field
            - `tlog_replicas` : the number of tlog replicas to create for this collection (solr 7.0+)
            - `pull_replicas` : the number of pull replicas to create for this collection (solr 7.0+)
            - `nrt_replicas` : the number of nrt replicas to create for this collection, by default solr creates NRT
                replicas if not defined. (solr 7.0+)
            - `auto_add_replicas`

        Additional parameters are further documented at
        https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-CreateaCollection
        Please check the collection management documentation for your specific version of solr to verify the arguments
        available.
        """
        params = self.get_params(**kwargs)
        params["action"] = "CREATE"

        # this collection doesn't exist yet, actually create it
        if not self.exists() or force:
            res = self.client.get("admin/collections", params).result
            if hasattr(res, "success"):
                # Create the index and wait until it's available
                while True:
                    if not self._is_index_created():
                        logging.getLogger("solrcloud").info(
                            "index not created yet, waiting..."
                        )
                        time.sleep(1)
                    else:
                        break
                    return SolrCollectionAdmin(self.connection, self.name)
            else:
                raise SolrException(str(res))

        # this collection is already present, just return it
        return SolrCollectionAdmin(self.connection, self.name)

    def _is_index_created(self) -> bool:
        """
        Whether the index was created
        :rtype: bool
        """
        server = list(self.connection.servers)[0]
        req = requests.get("%s/solr/%s" % (server, self.name))
        return req.status_code == requests.codes.ok

    def is_alias(self) -> bool:
        """
        Determines if this collection is an alias for a 'real' collection
        :rtype: bool
        """
        response = self.client.get(
            "/solr/admin/collections", {"action": "CLUSTERSTATUS", "wt": "json"}
        ).result.dict
        if "aliases" in response["cluster"]:
            return self.name in response["cluster"]["aliases"]
        return False

    def drop(self) -> SolrResponse:
        """
        Delete a collection

        :return: a response associated with the delete request
        :rtype: SolrResponse
        """
        return self.client.get(
            "admin/collections", {"action": "DELETE", "name": self.name}
        ).result

    def reload(self) -> SolrResponse:
        """
        Reload a collection

        :return: a response associated with the reload request
        :rtype: SolrResponse
        """
        return self.client.get(
            "admin/collections", {"action": "RELOAD", "name": self.name}
        ).result

    def split_shard(self, shard: str, ranges: str = None, split_key: str = None) -> SolrResponse:
        """
        Split a shard into two new shards

        :param shard: The name of the shard to be split.
        :type shard: str
        :param ranges: A comma-separated list of hash ranges in hexadecimal e.g. ranges=0-1f4,1f5-3e8,3e9-5dc
        :type ranges: str
        :param split_key: The key to use for splitting the index
        :type split_key: str
        :return: a response associated with the splitshard request
        :rtype: SolrResponse
        """
        params = {"action": "SPLITSHARD", "collection": self.name, "shard": shard}
        if ranges:
            params["ranges"] = ranges
        if split_key:
            params["split.key"] = split_key
        return self.client.get("admin/collections", params).result

    def create_shard(self, shard: str, create_node_set: str = None) -> SolrResponse:
        """
        Create a new shard

        :param shard: The name of the shard to be created.
        :type shard: str
        :param create_node_set: Allows defining the nodes to spread the new collection across.
        :type create_node_set: str
        :return: a response associated with the createshard request
        :rtype: SolrResponse
        """
        params = {"action": "CREATESHARD", "collection": self.name, "shard": shard}
        if create_node_set:
            params["create_node_set"] = create_node_set
        return self.client.get("admin/collections", params).result

    def create_alias(self, alias: str) -> SolrResponse:
        """
        Create or modify an alias for a collection

        :param alias: the name of the alias
        :type alias: str
        :return: a response associated with the createalias request
        :rtype: SolrResponse
        """
        params = {"action": "CREATEALIAS", "name": alias, "collections": self.name}
        return self.client.get("admin/collections", params).result

    def delete_alias(self, alias: str) -> SolrResponse:
        """
        Delete an alias for a collection

        :param alias: the name of the alias
        :type alias: str
        :return: a response associated with the deletealias request
        :rtype: SolrResponse
        """
        params = {"action": "DELETEALIAS", "name": alias}
        return self.client.get("admin/collections", params).result

    def delete_replica(self, replica: str, shard: str) -> SolrResponse:
        """
        Delete a replica

        :param replica:  The name of the replica to remove.
        :type replica: str
        :param shard: The name of the shard that includes the replica to be removed.
        :type shard: str
        :return: a response associated with the deletereplica request
        :rtype: SolrResponse
        """
        params = {
            "action": "DELETEREPLICA",
            "replica": replica,
            "collection": self.name,
            "shard": shard,
        }
        return self.client.get("admin/collections", params).result

    @property
    def state(self) -> dict[str, Any]:
        """
        Get the state of this collection

        :return: the state of this collection
        :rtype: dict
        """
        if self.is_alias():
            return {"warn": "no state info available for aliases"}

        response = self.client.get(
            "/{webappdir}/admin/collections".format(
                webappdir=self.connection.webappdir
            ),
            dict(action="clusterstatus"),
        ).result
        try:
            return response["cluster"]["collections"][self.name]
        except KeyError:
            return {}

    @property
    def shards(self) -> dict[str, Any]:
        """
        See state method
        :rtype: dict
        """
        return self.state

    @property
    def index_info(self) -> dict[str, Any]:
        """
        Get a high-level overview of this collection's index
        :return: information about an index
        :rtype:
        """
        response = self.client.get("%s/admin/luke" % self.name, {}).result
        # XXX ugly
        data = response["index"].dict
        data.pop("directory", None)
        data.pop("userData", None)
        return data

    @property
    def index_stats(self) -> SolrIndexStats:
        """
        Retrieves the SolrIndexStats class
        :return: SolrIndexStats class
        :rtype: SolrIndexStats
        """
        if self._index_stats is None:
            self._index_stats = SolrIndexStats(self.connection, self.name)
        return self._index_stats

    @property
    def schema(self):
        """
        Retrieves the SolrSchema class
        :return: SolrSchema class
        :rtype: SolrSchema
        """
        if self._schema is None:
            self._schema = SolrSchema(self.connection, self.name)
        return self._schema

    @property
    def stats(self) -> SolrIndexStats:
        """
        Alias for retrieving the SolrIndexStats class
        :return: SolrIndexStats class
        :rtype: SolrIndexStats
        """
        return self.index_stats

    def _backup_restore_action(
            self,
            action: str,
            backup_name: str,
            location: str = None,
            repository: str = None,
            max_num_backup_points: int = None,
            **kwargs
    ) -> AsyncResponse:
        """
        Creates or restores a backup for a collection, based on the action

        :param action: the action, either BACKUP or RESTORE
        :type action: str
        :param backup_name: the name of the backup we will use for storage & restoration
        :type backup_name: str
        :param location: an optional param to define where on the shared filesystem we should store the backup
        :type location: str
        :param repository: an optional param to define a repository type. filesystem is the default
        :type repository: str
        :return: an async response
        :rtype: AsyncResponse
        """
        params = self.get_params(**kwargs)
        params["action"] = action
        params["collection"] = self.name
        params["name"] = backup_name

        if location:
            params["location"] = location

        if repository:
            params["repository"] = repository

        if max_num_backup_points:
            params["maxNumBackupPoints"] = max_num_backup_points

        return self.client.get("admin/collections", params, asynchronous=True)

    def backup(
            self, backup_name: str, location: str = None, repository: str = None, max_num_backup_points: int = None
    ) -> AsyncResponse:
        """
        Creates a backup for a collection

        :param backup_name: the name of the backup we will use for storage & restoration
        :type backup_name: str
        :param location: an optional param to define where on the shared filesystem we should store the backup
        :type location: str
        :param repository: an optional param to define a repository type. filesystem is the default
        :type repository: str
        :param max_num_backup_points: The upper-bound on how many backups should be retained at the backup location.
        If the current number exceeds this bound, older backups will be deleted until only maxNumBackupPoints backups
        remain.
        This parameter has no effect if incremental=false is specified.
        :type max_num_backup_points: int
        :type repository: str
        :return: an async response
        :rtype: AsyncResponse
        """
        return self._backup_restore_action(
            "BACKUP",
            backup_name,
            location=location,
            repository=repository,
            max_num_backup_points=max_num_backup_points,
        )

    def list_backups(self, backup_name: str, location: str) -> dict[str, Any]:
        """
        List Backups for a collection
        :param backup_name: the name of the backup we will use for storage & restoration
        :type backup_name: str
        :param location: param to define where on the shared filesystem we should find the backup
        :type location: str
        :return: a list of backups
        :rtype: dict
        """
        params = {"action": "LISTBACKUP", "name": backup_name, "location": location}

        return self.client.get("admin/collections", params)

    def restore(self, backup_name: str, location: str = None, repository: str = None, **kwargs) -> AsyncResponse:
        """
        Restores a backup for a collection

        :param backup_name: the name of the backup we will use for restoration
        :type backup_name: str
        :param location: an optional param to define where on the shared filesystem we should access the backup
        :type location: str
        :param repository: an optional param to define a repository type. filesystem is the default
        :type repository: str
        :return: an async response
        :rtype: AsyncResponse
        """
        return self._backup_restore_action(
            "RESTORE", backup_name, location=location, repository=repository, **kwargs
        )

    def request_status(self, async_response: AsyncResponse = None, request_id: Union[str, uuid] = None) -> SolrResponse:
        """
        Retrieves the status of a request for a given async result
        :param async_response: the response object that includes its async_id
        :type async_response: AsyncResponse
        :param request_id: request_id in the response object for direct access
        :type request_id: UUID or str
        :return:
        """
        if not request_id:
            request_id = async_response.async_id
        if not isinstance(request_id, uuid.UUID):
            request_id = uuid.UUID(request_id)
        return self.client.get(
            "admin/collections",
            {
                "action": "REQUESTSTATUS",
                "requestid": request_id,
                "wt": "json",
            },
        ).result

    def request_state(self, async_response: AsyncResponse):
        """
        Retrieves the request state of a request for a given async result
        :param async_response: the response object that includes its async_id
        :type async_response: AsyncResponse
        :return:
        """
        return self.request_status(async_response).status.state
