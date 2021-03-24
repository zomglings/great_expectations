import os
import yaml
import uuid
from pprint import pprint

from humbug.consent import HumbugConsent
from humbug.report import Reporter, Modes, Report


from great_expectations import __version__ as ge_version



HUMBUG_TOKEN = "e10fbd54-71b0-4e68-80b0-d59ec3d99a81"
HUMBUG_KB_ID = "2e995d6c-95a9-4a35-8ee6-49846ac7fc63"
GE_REPORTING_CONFIG_FILE_NAME = "config_variables.yml"


def get_config_file_path():
    # Get working directory path
    working_dir = os.getcwd()

    config_file_path = os.path.join(working_dir, "great_expectations", "uncommitted", GE_REPORTING_CONFIG_FILE_NAME)

    return config_file_path


def save_reporting_config(consent: bool):
    """
    Allow or disallow Greate excpectations reporting.
    """
    reporting_config = get_config()
    if reporting_config:
        reporting_config["consent"] = consent
        try:
            with open(get_config_file_path(), "w") as ofp:
                yaml.dump(reporting_config, ofp)
        except Exception as err:
            print(err)
    return reporting_config

def get_config():
    config = {}
    config_path = get_config_file_path()
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r") as ifp:
                config = yaml.load(ifp)
            return config
        except Exception as err:
            print(err)
    return config


def get_reporting_config():

    config_report_path = get_config_file_path()

    if not os.path.exists(config_report_path):
        return {}

    config = get_config()
    if config is not None:
        if "consent"  not in config:    
            config = save_reporting_config(True)
    return config

def ge_consent_from_reporting_config_file() -> bool:
    reporting_config = get_reporting_config()
    return reporting_config.get("consent", False)


session_id = str(uuid.uuid4())
session_id_tag = "session_id:{}".format(session_id)

version_tag = f"version:{ge_version}-dev-reporting"


ge_version_tag = "version:{}".format(ge_version)
ge_tags = [ge_version_tag]




def get_reporter(mode=Modes.DEFAULT):
    
    client_id = get_reporting_config().get("client_id")
    ge_consent = HumbugConsent(ge_consent_from_reporting_config_file)
    ge_reporter = Reporter(
        name="great_expectation",
        consent=ge_consent,
        client_id=client_id,
        session_id=session_id,
        bugout_token=HUMBUG_TOKEN,
        bugout_journal_id=HUMBUG_KB_ID,
        mode=mode
    )
    return ge_reporter
