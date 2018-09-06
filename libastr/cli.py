# coding: utf-8
"""
libtestrail.cli
~~~~~~~~~~~~~~~

This module contains TestRail command line interface tools
"""

import ast
import click
import datetime
from libastr import Archive


@click.group(name='astr')
def astr():
    """
    ASTR Command Line Tools
    """


@astr.command(name='archive-test')
@click.argument('test_subject')
@click.argument('configuration', type=click.STRING)
@click.argument('paths', nargs=-1, type=click.STRING)
@click.option('--date', default=None, type=click.STRING,
              help='The date in the format dd/mm/yyyyy')
@click.option('--comments', default=None, type=click.STRING,
              help='comments about the test')
def archive(date, test_subject, configuration, paths, comments):
    """Archive a new test in ASTR.

        Args:
            date: test date (e.g. 2018-05-30)
            test_subject: type of test (e.g. MOTOR CONTROL)
            configuration: dictionary of configuration
                           (e.g. {"robot_type": "NAO", "robot_version": "V6"})
                           all the configurations of the test subject must be given
            paths: list of all the files to upload
                   (e.g. ["/home/john.doe/Desktop/measurement.csv",
                          "/home/john.doe/Desktop/analysis.png"])
            comments: (optional) comments about the test
    """
    if date is None:
        now = datetime.datetime.now()
        date = now.strftime("%d/%m/%Y")

    configuration = ast.literal_eval(configuration)

    archive = Archive(date, test_subject, configuration, comments=comments)
    archive.upload(paths)
