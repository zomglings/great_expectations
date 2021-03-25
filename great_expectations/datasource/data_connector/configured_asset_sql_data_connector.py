from typing import Dict, List, Optional

from great_expectations.core.batch import (
    BatchDefinition,
    BatchRequest,
    PartitionDefinition,
)
from great_expectations.datasource.data_connector.data_connector import DataConnector
from great_expectations.datasource.data_connector.util import (
    batch_definition_matches_batch_request,
)
from great_expectations.execution_engine import ExecutionEngine

try:
    import sqlalchemy as sa
except ImportError:
    sa = None


class ConfiguredAssetSqlDataConnector(DataConnector):
    """
    A DataConnector that requires explicit listing of SQL tables you want to connect to.

    Args:
        name (str): The name of this DataConnector
        datasource_name (str): The name of the Datasource that contains it
        execution_engine (ExecutionEngine): An ExecutionEngine
        data_assets (str): data_assets
    """

    def __init__(
        self,
        name: str,
        datasource_name: str,
        execution_engine: Optional[ExecutionEngine] = None,
        data_assets: Optional[Dict[str, dict]] = None,
    ):
        if data_assets is None:
            data_assets = {}
        self._data_assets = data_assets

        super().__init__(
            name=name,
            datasource_name=datasource_name,
            execution_engine=execution_engine,
        )

    @property
    def data_assets(self) -> Dict[str, dict]:
        return self._data_assets

    def add_data_asset(
        self,
        name: str,
        config: dict,
    ):
        """
        Add data_asset to DataConnector using data_asset name as key, and data_asset configuration as value.
        """
        self._data_assets[name] = config

    def _get_partition_definition_list_from_data_asset_config(
        self,
        data_asset_name,
        data_asset_config,
    ):
        if "table_name" in data_asset_config:
            table_name = data_asset_config["table_name"]
        else:
            table_name = data_asset_name

        if "splitter_method" in data_asset_config:
            splitter_fn = getattr(self, data_asset_config["splitter_method"])
            split_query = splitter_fn(
                table_name=table_name, **data_asset_config["splitter_kwargs"]
            )

            rows = self._execution_engine.engine.execute(split_query).fetchall()

            # Zip up split parameters with column names
            column_names = self._get_column_names_from_splitter_kwargs(
                data_asset_config["splitter_kwargs"]
            )
            partition_definition_list = [dict(zip(column_names, row)) for row in rows]

        else:
            partition_definition_list = [{}]

        return partition_definition_list

    def _refresh_data_references_cache(self):
        self._data_references_cache = {}

        for data_asset_name in self.data_assets:
            data_asset = self.data_assets[data_asset_name]
            partition_definition_list = (
                self._get_partition_definition_list_from_data_asset_config(
                    data_asset_name,
                    data_asset,
                )
            )

            # TODO Abe 20201029 : Apply sorters to partition_definition_list here
            # TODO Will 20201102 : add sorting code here
            self._data_references_cache[data_asset_name] = partition_definition_list

    def _get_column_names_from_splitter_kwargs(self, splitter_kwargs) -> List[str]:
        column_names: List[str] = []

        if "column_names" in splitter_kwargs:
            column_names = splitter_kwargs["column_names"]
        elif "column_name" in splitter_kwargs:
            column_names = [splitter_kwargs["column_name"]]

        return column_names

    def get_available_data_asset_names(self):
        """
        Return the list of asset names known by this DataConnector.

        Returns:
            A list of available names
        """
        return list(self.data_assets.keys())

    def get_unmatched_data_references(self) -> List[str]:
        """
        Returns the list of data_references unmatched by configuration by looping through items in _data_references_cache
        and returning data_reference that do not have an associated data_asset.

        Returns:
            list of data_references that are not matched by configuration.
        """
        return []

    def get_batch_definition_list_from_batch_request(self, batch_request: BatchRequest):
        self._validate_batch_request(batch_request=batch_request)

        if len(self._data_references_cache) == 0:
            self._refresh_data_references_cache()

        batch_definition_list: List[BatchDefinition] = []
        try:
            sub_cache = self._data_references_cache[batch_request.data_asset_name]
        except KeyError as e:
            raise KeyError(
                f"data_asset_name {batch_request.data_asset_name} is not recognized."
            )

        for partition_definition in sub_cache:
            batch_definition: BatchDefinition = BatchDefinition(
                datasource_name=self.datasource_name,
                data_connector_name=self.name,
                data_asset_name=batch_request.data_asset_name,
                partition_definition=PartitionDefinition(partition_definition),
            )
            if batch_definition_matches_batch_request(batch_definition, batch_request):
                batch_definition_list.append(batch_definition)

        return batch_definition_list

    def _get_data_reference_list_from_cache_by_data_asset_name(
        self, data_asset_name: str
    ) -> List[str]:
        return self._data_references_cache[data_asset_name]

    def _map_data_reference_to_batch_definition_list(
        self, data_reference, data_asset_name: Optional[str] = None  #: Any,
    ) -> Optional[List[BatchDefinition]]:
        # Note: This is a bit hacky, but it works. In sql_data_connectors, data references *are* dictionaries,
        # allowing us to invoke `PartitionDefinition(data_reference)`
        return [
            BatchDefinition(
                datasource_name=self.datasource_name,
                data_connector_name=self.name,
                data_asset_name=data_asset_name,
                partition_definition=PartitionDefinition(data_reference),
            )
        ]

    def _generate_batch_spec_parameters_from_batch_definition(
        self, batch_definition: BatchDefinition
    ) -> Dict:
        """
        Build BatchSpec parameters from batch_definition with the following components:
            1. data_asset_name from batch_definition
            2. partition_definition from batch_definition
            3. data_asset from data_connector

        Args:
            batch_definition (BatchDefinition): to be used to build batch_spec

        Returns:
            dict built from batch_definition
        """
        data_asset_name: str = batch_definition.data_asset_name
        return {
            "data_asset_name": data_asset_name,
            "table_name": data_asset_name,
            "partition_definition": batch_definition.partition_definition,
            **self.data_assets[data_asset_name],
        }

    # Splitter methods for listing partitions

    def _split_on_whole_table(
        self,
        table_name: str,
    ):
        """'Split' by returning the whole table

        Note: the table_name parameter is a required to keep the signature of this method consistent with other methods.
        """

        return sa.select([sa.true()])

    def _split_on_column_value(
        self,
        table_name: str,
        column_name: str,
    ):
        """Split using the values in the named column"""
        # query = f"SELECT DISTINCT(\"{self.column_name}\") FROM {self.table_name}"

        return sa.select([sa.func.distinct(sa.column(column_name))]).select_from(
            sa.text(table_name)
        )

    def _split_on_converted_datetime(
        self,
        table_name: str,
        column_name: str,
        date_format_string: str = "%Y-%m-%d",
    ):
        """Convert the values in the named column to the given date_format, and split on that"""
        # query = f"SELECT DISTINCT( strftime(\"{date_format_string}\", \"{self.column_name}\")) as my_var FROM {self.table_name}"

        return sa.select(
            [
                sa.func.distinct(
                    sa.func.strftime(
                        date_format_string,
                        sa.column(column_name),
                    )
                )
            ]
        ).select_from(sa.text(table_name))

    def _split_on_divided_integer(
        self, table_name: str, column_name: str, divisor: int
    ):
        """Divide the values in the named column by `divisor`, and split on that"""
        # query = f"SELECT DISTINCT(\"{self.column_name}\" / {divisor}) AS my_var FROM {self.table_name}"

        return sa.select(
            [sa.func.distinct(sa.cast(sa.column(column_name) / divisor, sa.Integer))]
        ).select_from(sa.text(table_name))

    def _split_on_mod_integer(self, table_name: str, column_name: str, mod: int):
        """Divide the values in the named column by `divisor`, and split on that"""
        # query = f"SELECT DISTINCT(\"{self.column_name}\" / {divisor}) AS my_var FROM {self.table_name}"

        return sa.select(
            [sa.func.distinct(sa.cast(sa.column(column_name) % mod, sa.Integer))]
        ).select_from(sa.text(table_name))

    def _split_on_multi_column_values(
        self,
        table_name: str,
        column_names: List[str],
    ):
        """Split on the joint values in the named columns"""
        # query = f"SELECT DISTINCT(\"{self.column_name}\") FROM {self.table_name}"

        return (
            sa.select([sa.column(column_name) for column_name in column_names])
            .distinct()
            .select_from(sa.text(table_name))
        )

    def _split_on_hashed_column(
        self,
        table_name: str,
        column_name: str,
        hash_digits: int,
    ):
        """Note: this method is experimental. It does not work with all SQL dialects."""
        # query = f"SELECT MD5(\"{self.column_name}\") = {matching_hash}) AS hashed_var FROM {self.table_name}"

        return sa.select([sa.func.md5(sa.column(column_name))]).select_from(
            sa.text(table_name)
        )
