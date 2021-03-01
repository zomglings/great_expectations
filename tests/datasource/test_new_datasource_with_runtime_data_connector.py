#
# @pytest.fixture
# def basic_pandas_datasource_v013(tmp_path_factory):
#     base_directory: str = str(
#         tmp_path_factory.mktemp(
#             "basic_pandas_datasource_v013_filesystem_data_connector"
#         )
#     )
#
#     basic_datasource: Datasource = instantiate_class_from_config(
#         yaml.load(
#             f"""
# class_name: Datasource
#
# execution_engine:
#     class_name: PandasExecutionEngine
#
# data_connectors:
#     test_runtime_data_connector:
#         module_name: great_expectations.datasource.data_connector
#         class_name: RuntimeDataConnector
#         runtime_keys:
#             - pipeline_stage_name
#             - airflow_run_id
#
#     my_filesystem_data_connector:
#         class_name: ConfiguredAssetFilesystemDataConnector
#         base_directory: {base_directory}
#         # TODO: <Alex>Investigate: this potentially breaks the data_reference centric design.</Alex>
#         glob_directive: "*.csv"
#         # glob_directive: "*"
#
#         assets:
#             Titanic: {{}}
#
#         default_regex:
#             # TODO: <Alex>Investigate: this potentially breaks the data_reference centric design.</Alex>
#             pattern: (.+)_(\\d+)\\.csv
#             # pattern: (.+)_(\\d+)\\.[a-z][a-z][a-z]
#             group_names:
#             - letter
#             - number
#     """,
#         ),
#         runtime_environment={"name": "my_datasource"},
#         config_defaults={"module_name": "great_expectations.datasource"},
#     )
#     return basic_datasource
