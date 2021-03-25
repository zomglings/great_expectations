.. _how_to_guides__validation__how_to_create_a_new_checkpoint:

How to create a new Checkpoint
==============================

This guide will help you create a new Checkpoint, which allows you to couple an Expectation Suite with a data set to validate.

**Note:** As of Great Expectations version 0.13.7, we refer to "class-based Checkpoints" as these are now fully implemented as their own Python class. This is mainly a change "behind the scenes". You can continue to use your existing legacy Checkpoint worfklows if you're working with concepts from the *stable* API (e.g. Datasources). If you're using concepts from the *experimental* API, please refer to the guides for class-based Checkpoints.

Steps
-----

.. content-tabs::

    .. tab-container:: tab0
        :title: Docs for Legacy Checkpoints (<=0.13.7)

        .. admonition:: Prerequisites: This how-to guide assumes you have already:

          - :ref:`Set up a working deployment of Great Expectations <tutorials__getting_started>`
          - :ref:`Configured a Datasource using the *stable* API <how_to_guides__configuring_datasources>`
          - :ref:`Created an Expectation Suite <how_to_guides__creating_and_editing_expectations>`


        1. First, run the CLI command below.

        .. code-block:: bash

            great_expectations checkpoint new my_checkpoint my_suite

        2. Next, you will be prompted to select a data asset you want to couple with the Expectation Suite. **Note**: The CLI currently only supports Datasources that are configured using the *stable* API. If you have set up a Datasource using the *experimental* API, please see the docs in the respective tab.
        3. You will then see a message that indicates the Checkpoint has been added to your project.

        .. code-block:: bash

            A checkpoint named `my_checkpoint` was added to your project!
            - To edit this checkpoint edit the checkpoint file: /home/ubuntu/my_project/great_expectations/checkpoints/my_checkpoint.yml
            - To run this checkpoint run `great_expectations checkpoint run my_checkpoint`


    .. tab-container:: tab1
        :title: Docs for Class-Based Checkpoints (>=0.13.8)

        .. admonition:: Prerequisites: This how-to guide assumes you have already:

          - :ref:`Set up a working deployment of Great Expectations <tutorials__getting_started>`
          - :ref:`Configured a Datasource using the *experimental* API <how_to_guides__configuring_datasources>`
          - :ref:`Created an Expectation Suite <how_to_guides__creating_and_editing_expectations>`

        1. **Instantiate a DataContext**

        The current version of class-based Checkpoints is not yet supported by the CLI. In order to configure and run Checkpoints, you will need to write some Python code. We suggest using a Jupyter notebook for convenience.

        Create a new Jupyter Notebook and instantiate a DataContext by running the following lines:

        .. code-block:: python

            import great_expectations as ge
            context = ge.get_context()

        2. **Create or copy a yaml config**

        You can create your own, or copy an example. For this example, we'll demonstrate using a basic Checkpoint configuration with the ``SimpleCheckpoint`` class, which takes care of some defaults. Replace all names such as ``my_datasource`` with the respective DataSource, DataConnector, DataAsset, and Expectation Suite names you have configured in your ``great_expectations.yml``.

        .. code-block:: python

            config = """
            name: my_checkpoint
            config_version: 1
            class_name: SimpleCheckpoint
            validations:
              - batch_request:
                  datasource_name: my_datasource
                  data_connector_name: my_data_connector
                  data_asset_name: MyDataAsset
                  partition_request:
                    index: -1
                expectation_suite_name: my_suite
            """

        This is the minimum required to configure a Checkpoint that will run the Expectation Suite ``my_suite`` against the data asset ``MyDataAsset``. See :ref:`how_to_guides_how_to_configure_a_new_checkpoint_using_test_yaml_config` for advanced configuration options.

        3. **Run context.test_yaml_config.**

        .. code-block:: python

            context.test_yaml_config(
                name="my_checkpoint",
                yaml_config=config,
            )

        When executed, ``test_yaml_config`` will instantiate the component and run through a ``self_check`` procedure to verify that the component works as expected.

        In the case of a Checkpoint, this means

            1. validating the `yaml` configuration,
            2. verifying that the Checkpoint class with the given configuration, if valid, can be instantiated, and
            3. printing warnings in case certain parts of the configuration, while valid, may be incomplete and need to be better specified for a successful Checkpoint operation.

        The output will look something like this:

        .. code-block:: bash

            Attempting to instantiate class from config...
            Instantiating as a SimpleCheckpoint, since class_name is SimpleCheckpoint
            Successfully instantiated SimpleCheckpoint


            Checkpoint class name: SimpleCheckpoint

        If something about your configuration wasn't set up correctly, ``test_yaml_config`` will raise an error.

        4. **Store your Checkpoint config.**

        After you are satisfied with your configuration, save it using the following snippet:

        .. code-block:: python


            from ruamel.yaml import YAML
            yaml = YAML()
            context.add_checkpoint(**yaml.load(config))

        5. **Check your stored Checkpoint config.**

        If the Store Backend of your Checkpoint Store is on the local filesystem, you can navigate to the ``checkpoints`` store directory that is configured in ``great_expectations.yml`` and find the configuration files corresponding to the Checkpoints you created.

        6. **(Optional:) Test running the new Checkpoint.**

        Now that you have stored your Checkpoint configuration to the Store backend configured for the Checkpoint Configuration store of your Data Context, you can also test ``context.run_checkpoint``, right within your notebook:

        .. code-block:: python

            checkpoint_run_result = context.run_checkpoint(
                checkpoint_name="my_checkpoint",
            )


        Before running a Checkpoint, make sure that all classes and Expectation Suites referred to in the configuration exist.

        When ``run_checkpoint`` returns, the ``checkpoint_run_result`` can then be checked for the value of the ``success`` field (all validations passed) and other information associated with running the specified actions.



        **For more advanced configurations of Checkpoints, please see** :ref:`how_to_guides_how_to_configure_a_new_checkpoint_using_test_yaml_config`.


Additional Resources
--------------------
- :ref:`Check out the detailed tutorial on Checkpoints <tutorials__getting_started__validate_your_data>`


.. discourse::
    :topic_identifier: 220
