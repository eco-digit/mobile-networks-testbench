# ECO:DIGIT (Industrial) Mobile Networks energy estimation
#
# Copyright Siemens AG, 2023-2026. Part of the ECO:DIGIT Project.
#
# This program and the accompanying materials are made
# available under the terms of the MIT License, which is
# available at https://opensource.org/licenses/MIT
#
# SPDX-FileCopyrightText: 2026 Siemens AG
# SPDX-License-Identifier: MIT

import json
from datetime import datetime, date

class InputParameterParser:
    def __init__(self, input_parameters_file):
        self.input_parameters_file = input_parameters_file
        self.input_parameters = self.parse_input_parameters()
        self.template_file = self.get_template()

    def parse_input_parameters(self):
        """
        Parse the input parameters from the input_parameters_file

        Returns
        -------
        dict
            Input parameters.
        """
        with open(self.input_parameters_file) as json_file:
            input_parameters = json.load(json_file)
        return input_parameters

    def get_template(self):
        """
        Get the template from the input parameters.

        Returns
        -------
        str
            Template.
        """
        return self.input_parameters["template"]

class TemplateParser:
    def __init__(self, template_file):
        self.template_file = template_file
        self.template = self.parse_template()

    def parse_template(self):
        """
        Parse the template from the template_file

        Returns
        -------
        dict
            Template.
        """
        with open(self.template_file) as json_file:
            template = json.load(json_file)
        return template
    
def dump_output_json(output_object, output_json_file, indent=4):
    """
    Dump the output json to the output json file.

    Parameters
    ----------
    output_json : dict
        Output json.
    output_json_file : str
        Output json file.
    """
    with open(output_json_file, 'w') as json_file:
        json.dump(output_object.__dict__, json_file, indent=indent, default=json_serialize_datetime)

def json_serialize_datetime(obj):
    """
    JSON serializer for datetime and date objects.

    Parameters
    ----------
    obj : datetime or date
        Object to serialize.

    Returns
    -------
    str
        ISO format string of the datetime or date object.
    """
    if isinstance(obj, datetime) or isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")