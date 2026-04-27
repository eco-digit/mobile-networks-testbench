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


class Switch():
    def __init__(self,
                 duration_evaluated_seconds):
        # power consumption
        self.power_consumption_W = 9.6
        self.maximum_power_consumption_W = self.power_consumption_W
        self.idle_power_consumption_W = self.power_consumption_W
        self.dynamic_power_consumption_W = self.power_consumption_W

        # calculate energy consumption
        self.duration_evaluated_seconds = duration_evaluated_seconds

        # calculate energy consumption
        self.energy_consumption_Wh = self.power_consumption_W * self.duration_evaluated_seconds / 3600