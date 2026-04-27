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

class Network5G:
    def __init__(self,
                 duration_evaluated_seconds: float,
                 radio_units: list,
                 user_equipments: list,
                 distributed_centralized_units: list,
                 core_network_servers: list,
                 switches: list):

        self.duration_evaluated_sec = duration_evaluated_seconds

        # helpers to safely sum attributes that might be missing
        def _sum_attr(items, attr):
            return sum(getattr(it, attr, 0) for it in (items or []))

        # per-category energy (Wh)
        self.radio_units_energy_consumption_Wh = _sum_attr(radio_units, "energy_consumption_Wh")
        self.user_equipments_energy_consumption_Wh = _sum_attr(user_equipments, "energy_consumption_Wh")
        self.distributed_centralized_units_energy_consumption_Wh = _sum_attr(distributed_centralized_units, "energy_consumption_Wh")
        self.core_network_servers_energy_consumption_Wh = _sum_attr(core_network_servers, "energy_consumption_Wh")
        self.switches_energy_consumption_Wh = _sum_attr(switches, "energy_consumption_Wh")

        # totals
        self.total_energy_consumption_Wh = (
            self.radio_units_energy_consumption_Wh
            + self.user_equipments_energy_consumption_Wh
            + self.distributed_centralized_units_energy_consumption_Wh
            + self.core_network_servers_energy_consumption_Wh
            + self.switches_energy_consumption_Wh
        )