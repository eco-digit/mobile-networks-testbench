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

class UserEquipment():
    def __init__(self,
                 downlink_load_distribution: dict,
                 uplink_load_distribution: dict,
                 duration_evaluated_sec: float,
                 part_slots_downlink: float,
                 part_slots_uplink: float):
        self.downlink_load_distribution = downlink_load_distribution
        self.uplink_load_distribution = uplink_load_distribution
        self.duration_evaluated_sec = duration_evaluated_sec

        power_consumption_idle_W = 0.3
        power_consumption_receive_W = 13.2
        power_consumption_transmit_W = 13.2

        # calculate energy consumption
        self.energy_consumption_Wh = 0
        for load, prob in self.downlink_load_distribution.items():
            if load < 0.05:
                power_consumption_W = power_consumption_idle_W
            else:
                power_consumption_W = power_consumption_receive_W
            time_h = (part_slots_downlink * self.duration_evaluated_sec) / 3600
            energy_Wh = power_consumption_W * time_h * prob
            self.energy_consumption_Wh += energy_Wh

        for load, prob in self.uplink_load_distribution.items():
            if load < 0.05:
                power_consumption_W = power_consumption_idle_W
            else:
                power_consumption_W = power_consumption_transmit_W
            time_h = (part_slots_uplink * self.duration_evaluated_sec) / 3600
            energy_Wh = power_consumption_W * time_h * prob
            self.energy_consumption_Wh += energy_Wh


class RadioUnit():
    def __init__(self, 
                downlink_load_distribution: dict,
                uplink_load_distribution: dict,
                duration_evaluated_sec: float,
                part_slots_downlink: float,
                part_slots_uplink: float):
        
        self.downlink_load_distribution = downlink_load_distribution
        self.uplink_load_distribution = uplink_load_distribution
        self.duration_evaluated_sec = duration_evaluated_sec

        power_consumption_idle_W = 34
        power_consumption_receive_W = 36.2
        power_consumption_transmit_W = 36.2

        # calculate energy consumption
        self.energy_consumption_Wh = 0
        for load, prob in self.downlink_load_distribution.items():
            if load < 0.05:
                power_consumption_W = power_consumption_idle_W
            else:
                power_consumption_W = power_consumption_receive_W
            time_h = (part_slots_downlink * self.duration_evaluated_sec) / 3600
            energy_Wh = power_consumption_W * time_h * prob
            self.energy_consumption_Wh += energy_Wh

        for load, prob in self.uplink_load_distribution.items():
            if load < 0.05:
                power_consumption_W = power_consumption_idle_W
            else:
                power_consumption_W = power_consumption_transmit_W
            time_h = (part_slots_uplink * self.duration_evaluated_sec) / 3600
            energy_Wh = power_consumption_W * time_h * prob
            self.energy_consumption_Wh += energy_Wh

        
class DistributedCentralizedUnit():
    def __init__(self, duration_evaluated_sec):
        self.duration_evaluated_sec = duration_evaluated_sec

        self.power_consumption_W = 250

        # calculate energy consumption
        self.energy_consumption_Wh = self.power_consumption_W * self.duration_evaluated_sec / 3600

class CoreNetworkServer():
    def __init__(self, duration_evaluated_sec):
        self.duration_evaluated_sec = duration_evaluated_sec

        self.power_consumption_W = 150

        # calculate energy consumption
        self.energy_consumption_Wh = self.power_consumption_W * self.duration_evaluated_sec / 3600

