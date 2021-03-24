import click

from great_expectations.cli.v012 import toolkit

from great_expectations.core.reporting import get_reporter, save_reporting_config, Report


@click.command()
@click.option("--on/--off", help="Turn crash report on/off", default=True)
def reporting(on: bool) -> None:
    """
    Enable or disable sending crash reports to Great Expectations team/superconductive.
    """
    toolkit.load_data_context_with_error_handling(None)
    ge_reporter = get_reporter()
    report = Report(
        title="Consent change",
        tags=ge_reporter.system_tags(),
        content="Consent? `{}`".format(on),
    )
    ge_reporter.publish(report)
    save_reporting_config(on)