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

import math

class RadioResourceUtilization5G:
    """Utilities for 5G radio resource calculations."""

    @staticmethod
    def calculate_load_distribution(
        target_downlink_data_rate_distribution_Mbps: dict,
        target_uplink_data_rate_distribution_Mbps: dict,
        available_prbs: int,
        modulation_order: int,
        coding_rate: float,
        slot_duration_ms = 1,
        symbols_per_slot=14,
        overhead_fraction=0.1,
        subcarriers_per_prb=12,
        mimo_layers_downlink=1,
        mimo_layers_uplink=1,
        aggregated_carriers=1,
        beams_mumimo=1,
        scaling_factor_downlink=1,
        scaling_factor_uplink=1):
        """
        Calculate the load distribution in terms of PRBs for downlink and uplink.

        Parameters
        ----------

        - target_downlink_data_rate_distribution_Mbps: Dict mapping target downlink data rates (Mbps) to their probabilities
        - target_uplink_data_rate_distribution_Mbps: Dict mapping target uplink data rates (Mbps) to their probabilities
        - available_prbs: Total number of available PRBs
        - modulation_order: Bits per symbol (e.g., QPSK=2, 16QAM=4, 64QAM=6, 256QAM=8)
        - coding_rate: Fraction of bits used for data (e.g., 0.75)
        - slot_duration_ms: Duration of a slot in milliseconds (default: 1 ms)
        - symbols_per_slot: Number of OFDM symbols per slot (default: 14)
        - overhead_fraction: Fraction of symbols lost to overhead (default: 10%)
        - subcarriers_per_prb: Number of subcarriers per PRB (default: 12)
        - mimo_layers_downlink: Number of MIMO layers for downlink (default: 1)
        - mimo_layers_uplink: Number of MIMO layers for uplink (default: 1)
        - aggregated_carriers: Number of aggregated carriers (default: 1)
        - beams_mumimo: Number of beams in MU-MIMO (default: 1)
        - scaling_factor_downlink: Scaling factor for downlink (default: 1)
        - scaling_factor_uplink: Scaling factor for uplink (default: 1)

        Returns
        -------
        - downlink_load_distribution: Dict mapping target downlink data rates to required PRBs
        - uplink_load_distribution: Dict mapping target uplink data rates to required PRBs
        """
        downlink_load_distribution = {}
        uplink_load_distribution = {}

        for data_rate_mbps, probability in target_downlink_data_rate_distribution_Mbps.items():
            prbs_required = RadioResourceUtilization5G.calculate_prbs_required(
                target_data_rate_mbps=data_rate_mbps,
                modulation_order=modulation_order,
                coding_rate=coding_rate,
                slot_duration_ms=slot_duration_ms,
                symbols_per_slot=symbols_per_slot,
                overhead_fraction=overhead_fraction,
                subcarriers_per_prb=subcarriers_per_prb,
                scaling_factor=scaling_factor_downlink,
                mimo_layers=mimo_layers_downlink,
                aggregated_carriers=aggregated_carriers,
                beams_mumimo=beams_mumimo
            )

            load = round(prbs_required / available_prbs, 2)
            if load > 1.0:
                load = 1.0
            if not load in downlink_load_distribution:
                downlink_load_distribution[load] = probability
            else:
                downlink_load_distribution[load] += probability


        for data_rate_mbps, probability in target_uplink_data_rate_distribution_Mbps.items():
            prbs_required = RadioResourceUtilization5G.calculate_prbs_required(
                target_data_rate_mbps=data_rate_mbps,
                modulation_order=modulation_order,
                coding_rate=coding_rate,
                slot_duration_ms=slot_duration_ms,
                symbols_per_slot=symbols_per_slot,
                overhead_fraction=overhead_fraction,
                subcarriers_per_prb=subcarriers_per_prb,
                scaling_factor=scaling_factor_uplink,
                mimo_layers=mimo_layers_uplink,
                aggregated_carriers=aggregated_carriers,
                beams_mumimo=beams_mumimo
            )
            load = round(prbs_required / available_prbs, 2)
            if load > 1.0:
                load = 1.0
            if not load in uplink_load_distribution:
                uplink_load_distribution[load] = probability
            else:
                uplink_load_distribution[load] += probability

        return downlink_load_distribution, uplink_load_distribution

    @staticmethod
    def calculate_prbs_required(
        target_data_rate_mbps,
        modulation_order,
        coding_rate,
        slot_duration_ms=1,
        symbols_per_slot=14,
        overhead_fraction=0.1,
        subcarriers_per_prb=12,
        scaling_factor=1,
        mimo_layers=1,
        aggregated_carriers=1,
        beams_mumimo=1,
    ):
        """
        Calculate the number of PRBs required to achieve a target data rate in 5G.

        Parameters
        ----------
        - target_data_rate_mbps: Target data rate in Mbps
        - modulation_order: Bits per symbol (e.g., QPSK=2, 16QAM=4, 64QAM=6, 256QAM=8)
        - coding_rate: Fraction of bits used for data (e.g., 0.75)
        - slot_duration_ms: Duration of a slot in milliseconds (default: 1 ms)
        - symbols_per_slot: Number of OFDM symbols per slot (default: 14)
        - overhead_fraction: Fraction of symbols lost to overhead (default: 10%)
        - subcarriers_per_prb: Number of subcarriers per PRB (default: 12)
        - scaling_factor: Scaling factor (default: 1)
        - mimo_layers: Number of MIMO layers (default: 1)
        - aggregated_carriers: Number of aggregated carriers (default: 1)
        - beams_mumimo: Number of beams in MU-MIMO (default: 1        

        Returns
        -------
        - Number of PRBs required (int)
        """
        # Convert Mbps to bits per slot
        target_data_rate_bps = target_data_rate_mbps * 1_000_000
        target_data_rate_per_slot = target_data_rate_bps * (slot_duration_ms / 1000)

        # Calculate usable symbols per slot
        usable_symbols = symbols_per_slot * (1 - overhead_fraction)
        bits_per_prb = (modulation_order * coding_rate * usable_symbols * subcarriers_per_prb)

        # Adjust for MIMO, aggregated carriers, and MU-MIMO beams
        bits_per_prb *= (mimo_layers * aggregated_carriers * beams_mumimo * scaling_factor)

        # Calculate required PRBs
        prbs_required = math.ceil(target_data_rate_per_slot / bits_per_prb)

        return prbs_required