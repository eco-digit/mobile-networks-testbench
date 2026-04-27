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

"""
Calculates the power and energy consumption of a 5G network based on the infrastructure definition, 
radio resource models and power consumption models.

Usage: main.py INPUT OUTPUT

Arguments:
    INPUT     input parameter json file
    OUTPUT    output directory
"""

import os

# import docopt
try:
    from docopt import docopt
except ImportError:
    exit(
        "This requires that `docopt` command-line interface"
        " is installed: \n    pip install docopt\n"
    )

# import schema
try:
    from schema import And
    from schema import Schema
    from schema import SchemaError
    from schema import Use
except ImportError:
    exit(
        "This requires that `schema` data-validation library"
        " is installed: \n    pip install schema\n"
        "https://github.com/halst/schema"
    )

# import utilities
from utilities.parameter_parser import InputParameterParser
from utilities.parameter_parser import TemplateParser
from utilities.parameter_parser import dump_output_json
from utilities.pcap_analyzer import PcapAnalyzer
from utilities.tcpdump_analyzer import TcpDumpAnalyzer

# import infrastructure models
import infrastructure_models.nr_5g.network_model_5g as network_model_5g
import infrastructure_models.nr_5g.hardware_5g as hardware_5g
import infrastructure_models.generic_network_hardware as generic_network_hardware
import radio_resource_models.nr_radio_resource_model as nr_radio_resource_model

args = docopt(__doc__)

schema = Schema(
    {
        "INPUT": And(os.path.isfile, error="INPUT should be readable"),
        "OUTPUT": And(os.path.exists, error="OUTPUT should exist"),
    }
)
try:
    args = schema.validate(args)
except SchemaError as e:
    print("Error: ", e)
    exit(e)

input_file = args["INPUT"]
output_path = args["OUTPUT"]

# parse input parameter json
input_parser = InputParameterParser(input_file)
# parse template json
template_parser = TemplateParser(input_parser.template_file)

traffic_input_mode = input_parser.input_parameters["loadProfile"]["trafficInputMode"]

if traffic_input_mode == "pcap":
    pcap_file = input_parser.input_parameters["loadProfile"]["pcap"]["pcapFile"]
    pcap_clients_ips = input_parser.input_parameters["loadProfile"]["pcap"]["pcapIPClients"]
    pcap_servers_ips = input_parser.input_parameters["loadProfile"]["pcap"]["pcapIPServers"]

    # Pcap analyzer
    pcap_metrics = PcapAnalyzer(pcap_file, pcap_clients_ips, pcap_servers_ips)

    # Use the metrics from the pcap analyzer
    UPLINK_PACKET_SIZE_DISTRIBUTION_BYTES = pcap_metrics.uplink_packet_size_bytes_distribution
    DOWNLINK_PACKET_SIZE_DISTRIBUTION_BYTES = pcap_metrics.downlink_packet_size_bytes_distribution
    UPLINK_PACKET_RATE_DISTRIBUTION = pcap_metrics.uplink_packet_rate_distribution
    DOWNLINK_PACKET_RATE_DISTRIBUTION = pcap_metrics.downlink_packet_rate_distribution

    print("\nPCAP ANALYZER")
    print("----------------")
    print("Duration (s): ", pcap_metrics.capture_duration)
    print("Total Packets: ", pcap_metrics.total_number_of_packets)

    # duration to be evaluated is the duration of the pcap
    DURATION_EVALUATED_SEC = pcap_metrics.capture_duration
    print("Using duration for energy calcuation from PCAP file: ", DURATION_EVALUATED_SEC, " seconds")

elif traffic_input_mode == "tcpdump":
    tcpdump_file = input_parser.input_parameters["loadProfile"]["tcpdump"]["tcpdumpFile"]
    tcpdump_clients_ips = input_parser.input_parameters["loadProfile"]["tcpdump"]["tcpdumpIPClients"]
    tcpdump_servers_ips = input_parser.input_parameters["loadProfile"]["tcpdump"]["tcpdumpIPServers"]

    # Tcpdump analyzer
    tcpdump_metrics = TcpDumpAnalyzer(tcpdump_file, tcpdump_clients_ips, tcpdump_servers_ips)

    # Use the metrics from the tcpdump analyzer
    UPLINK_PACKET_SIZE_DISTRIBUTION_BYTES = tcpdump_metrics.uplink_packet_size_bytes_distribution
    DOWNLINK_PACKET_SIZE_DISTRIBUTION_BYTES = tcpdump_metrics.downlink_packet_size_bytes_distribution
    UPLINK_PACKET_RATE_DISTRIBUTION = tcpdump_metrics.uplink_packet_rate_distribution
    DOWNLINK_PACKET_RATE_DISTRIBUTION = tcpdump_metrics.downlink_packet_rate_distribution

    print("\nTCPDUMP ANALYZER")
    print("----------------")
    print("Duration (s): ", tcpdump_metrics.capture_duration)
    print("Total Packets: ", tcpdump_metrics.total_number_of_captured_packets)

    # duration to be evaluated is the duration of the tcpdump
    DURATION_EVALUATED_SEC = tcpdump_metrics.capture_duration
    print("Using duration for energy calcuation from tcpdump TXT file: ", DURATION_EVALUATED_SEC, " seconds")

    # Exclude packets from the output JSON, as they are not needed
    del tcpdump_metrics.packets
    del tcpdump_metrics.uplink_packets
    del tcpdump_metrics.downlink_packets
    dump_output_json(tcpdump_metrics, os.path.join(output_path, "tcpdump_analyzer.json"))

elif traffic_input_mode == "distribution":
    # manual entry mode of load model with distributions, use these directly
    UPLINK_PACKET_SIZE_BYTES = input_parser.input_parameters["loadProfile"]["distribution"]["packetSizeUplink_bytes"]
    DOWNLINK_PACKET_SIZE_BYTES = input_parser.input_parameters["loadProfile"]["distribution"]["packetSizeDownlink_bytes"]
    UPLINK_PACKET_SIZE_PROBABILITY = input_parser.input_parameters["loadProfile"]["distribution"]["packetSizeUplinkProbability"]
    DOWNLINK_PACKET_SIZE_PROBABILITY = input_parser.input_parameters["loadProfile"]["distribution"]["packetSizeDownlinkProbability"]
    UPLINK_PACKET_SIZE_DISTRIBUTION_BYTES = dict(zip(UPLINK_PACKET_SIZE_BYTES, UPLINK_PACKET_SIZE_PROBABILITY))
    DOWNLINK_PACKET_SIZE_DISTRIBUTION_BYTES = dict(zip(DOWNLINK_PACKET_SIZE_BYTES   , DOWNLINK_PACKET_SIZE_PROBABILITY))
    UPLINK_PACKET_RATE = input_parser.input_parameters["loadProfile"]["distribution"]["packetRateUplink_packets_per_second"]
    DOWNLINK_PACKET_RATE = input_parser.input_parameters["loadProfile"]["distribution"]["packetRateDownlink_packets_per_second"]
    UPLINK_PACKET_RATE_PROBABILITY = input_parser.input_parameters["loadProfile"]["distribution"]["packetRateUplinkProbability"]
    DOWNLINK_PACKET_RATE_PROBABILITY = input_parser.input_parameters["loadProfile"]["distribution"]["packetRateDownlinkProbability"]
    UPLINK_PACKET_RATE_DISTRIBUTION = dict(zip(UPLINK_PACKET_RATE, UPLINK_PACKET_RATE_PROBABILITY))
    DOWNLINK_PACKET_RATE_DISTRIBUTION = dict(zip(DOWNLINK_PACKET_RATE, DOWNLINK_PACKET_RATE_PROBABILITY))
    # duration to be evaluated is also given
    DURATION_EVALUATED_SEC = input_parser.input_parameters["loadProfile"]["distribution"]["durationEvaluated_sec"]
    print("Using duration for energy calculation from input parameters: ", DURATION_EVALUATED_SEC, " seconds")
else:
    raise ValueError("Invalid load model traffic input mode")

print("\nLOAD PROFILE DISTRIBUTIONS")
print("----------------")
print("Uplink Packet Size Distribution (bytes): ", UPLINK_PACKET_SIZE_DISTRIBUTION_BYTES)
print("Downlink Packet Size Distribution (bytes): ", DOWNLINK_PACKET_SIZE_DISTRIBUTION_BYTES)
print("Uplink Packet Rate Distribution (packets/s): ", UPLINK_PACKET_RATE_DISTRIBUTION)
print("Downlink Packet Rate Distribution (packets/s): ", DOWNLINK_PACKET_RATE_DISTRIBUTION)

# Calculate data rate distribution for uplink and downlink
DOWNLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S = {}
for downlink_packet_size_bytes, downlink_prob in DOWNLINK_PACKET_SIZE_DISTRIBUTION_BYTES.items():
    for downlink_packet_rate, downlink_packet_rate_prob in DOWNLINK_PACKET_RATE_DISTRIBUTION.items():
        downlink_data_rate = downlink_packet_size_bytes * downlink_packet_rate / 1e6
        downlink_data_rate = round(downlink_data_rate, 0)
        if downlink_data_rate in DOWNLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S:
            DOWNLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S[downlink_data_rate] += downlink_prob * downlink_packet_rate_prob
        else:
            DOWNLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S[downlink_data_rate] = downlink_prob * downlink_packet_rate_prob

UPLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S = {}
for uplink_packet_size_bytes, uplink_prob in UPLINK_PACKET_SIZE_DISTRIBUTION_BYTES.items():
    for uplink_packet_rate, uplink_packet_rate_prob in UPLINK_PACKET_RATE_DISTRIBUTION.items():
        uplink_data_rate = uplink_packet_size_bytes * uplink_packet_rate / 1e6
        uplink_data_rate = round(uplink_data_rate, 0)
        if uplink_data_rate in UPLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S:
            UPLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S[uplink_data_rate] += uplink_prob * uplink_packet_rate_prob
        else:
            UPLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S[uplink_data_rate] = uplink_prob * uplink_packet_rate_prob

DOWNLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S = {}
for data_rate, prob in DOWNLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S.items():
    number_of_ues_per_cell = input_parser.input_parameters["loadProfile"]["numberUserEquipmentsPerCell"]
    total_data_rate = data_rate * number_of_ues_per_cell
    if total_data_rate in DOWNLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S:
        DOWNLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S[total_data_rate] += prob
    else:
        DOWNLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S[total_data_rate] = prob

UPLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S = {}
for data_rate, prob in UPLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S.items():
    number_of_ues_per_cell = input_parser.input_parameters["loadProfile"]["numberUserEquipmentsPerCell"]
    total_data_rate = data_rate * number_of_ues_per_cell
    if total_data_rate in UPLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S:
        UPLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S[total_data_rate] += prob
    else:
        UPLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S[total_data_rate] = prob

print("\nDATA RATE DISTRIBUTIONS")
print("----------------")
print("Downlink Data Rate Distribution per UE (Mbps): ", DOWNLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S)
print("Uplink Data Rate Distribution per UE (Mbps): ", UPLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S)
print("Downlink Data Rate Distribution per Cell (Mbps): ", DOWNLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S)
print("Uplink Data Rate Distribution per Cell (Mbps): ", UPLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S)

# Radio resource model
downlink_per_cell_load_distribution, uplink_per_cell_load_distribution = nr_radio_resource_model.RadioResourceUtilization5G.calculate_load_distribution(
    target_downlink_data_rate_distribution_Mbps=DOWNLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S,
    target_uplink_data_rate_distribution_Mbps=UPLINK_DATA_RATE_DISTRIBUTION_PER_CELL_MBIT_S,
    available_prbs=template_parser.template["radioResourceParameters"]["availablePRBs"],
    modulation_order=template_parser.template["radioResourceParameters"]["modulationOrder"],
    coding_rate=template_parser.template["radioResourceParameters"]["codingRate"],
    slot_duration_ms=template_parser.template["radioResourceParameters"]["slotDuration_ms"],
    overhead_fraction=template_parser.template["radioResourceParameters"]["overheadFraction"],
    subcarriers_per_prb=template_parser.template["radioResourceParameters"]["subcarriersPerPRB"],
    scaling_factor_uplink=template_parser.template["radioResourceParameters"]["scalingFactorUplink"],
    scaling_factor_downlink=template_parser.template["radioResourceParameters"]["scalingFactorDownlink"],
    mimo_layers_downlink=template_parser.template["radioResourceParameters"]["mimoLayersDownlink"],
    mimo_layers_uplink=template_parser.template["radioResourceParameters"]["mimoLayersUplink"],
    aggregated_carriers=template_parser.template["radioResourceParameters"]["numberOfAggregatedCarriers"],
    beams_mumimo=template_parser.template["radioResourceParameters"]["beamsMUMIMO"]
)

downlink_per_ue_load_distribution, uplink_per_ue_load_distribution = nr_radio_resource_model.RadioResourceUtilization5G.calculate_load_distribution(
    target_downlink_data_rate_distribution_Mbps=DOWNLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S,
    target_uplink_data_rate_distribution_Mbps=UPLINK_DATA_RATE_DISTRIBUTION_PER_UE_MBIT_S,
    available_prbs=template_parser.template["radioResourceParameters"]["availablePRBs"],
    modulation_order=template_parser.template["radioResourceParameters"]["modulationOrder"],
    coding_rate=template_parser.template["radioResourceParameters"]["codingRate"],
    slot_duration_ms=template_parser.template["radioResourceParameters"]["slotDuration_ms"],
    symbols_per_slot=template_parser.template["radioResourceParameters"]["symbolsPerSlot"],
    overhead_fraction=template_parser.template["radioResourceParameters"]["overheadFraction"],
    subcarriers_per_prb=template_parser.template["radioResourceParameters"]["subcarriersPerPRB"],
    scaling_factor_uplink=template_parser.template["radioResourceParameters"]["scalingFactorUplink"],
    scaling_factor_downlink=template_parser.template["radioResourceParameters"]["scalingFactorDownlink"],
    mimo_layers_downlink=template_parser.template["radioResourceParameters"]["mimoLayersDownlink"],
    mimo_layers_uplink=template_parser.template["radioResourceParameters"]["mimoLayersUplink"],
    aggregated_carriers=template_parser.template["radioResourceParameters"]["numberOfAggregatedCarriers"],
    beams_mumimo=template_parser.template["radioResourceParameters"]["beamsMUMIMO"]
)

print("\nLOAD DISTRIBUTIONS")
print("----------------")
print("Downlink Load Distribution per Cell: ", downlink_per_cell_load_distribution)
print("Uplink Load Distribution per Cell: ", uplink_per_cell_load_distribution)
print("Downlink Load Distribution per UE: ", downlink_per_ue_load_distribution)
print("Uplink Load Distribution per UE: ", uplink_per_ue_load_distribution)

number_of_ues_per_cell = input_parser.input_parameters["loadProfile"]["numberUserEquipmentsPerCell"]
number_of_radio_units = template_parser.template["networkParameters"]["numberRadioUnits"]
number_of_distributed_centralized_units = template_parser.template["networkParameters"]["numberDistributedCentralizedUnits"]
number_of_core_servers = template_parser.template["networkParameters"]["numberCoreServers"]
number_of_switches = template_parser.template["networkParameters"]["numberSwitches"]
cells_per_radio_unit = template_parser.template["networkParameters"]["cellsPerRadioUnit"]
part_slots_downlink = template_parser.template["radioResourceParameters"]["partSlotsDownlink"]
part_slots_uplink = template_parser.template["radioResourceParameters"]["partSlotsUplink"]

# create lists of devices sized according to the input parameters
total_ues = number_of_ues_per_cell * number_of_radio_units * cells_per_radio_unit
ues = [hardware_5g.UserEquipment(downlink_load_distribution=downlink_per_ue_load_distribution,
                                  uplink_load_distribution=uplink_per_ue_load_distribution,
                                    part_slots_downlink=part_slots_downlink,
                                    part_slots_uplink=part_slots_uplink,
                                  duration_evaluated_sec=DURATION_EVALUATED_SEC) for _ in range(total_ues)]
for idx, ue_inst in enumerate(ues, start=1):
    dump_output_json(ue_inst, os.path.join(output_path, f"user_equipment_5g_{idx}.json"))

rus = [
    hardware_5g.RadioUnit(downlink_load_distribution=downlink_per_cell_load_distribution,
                           uplink_load_distribution=uplink_per_cell_load_distribution,
                            part_slots_downlink=part_slots_downlink,
                            part_slots_uplink=part_slots_uplink,
                           duration_evaluated_sec=DURATION_EVALUATED_SEC)
    for _ in range(number_of_radio_units)
]
for idx, ru in enumerate(rus, start=1):
    dump_output_json(ru, os.path.join(output_path, f"radio_unit_5g_{idx}.json"))

cu_dus = [
    hardware_5g.DistributedCentralizedUnit(duration_evaluated_sec=DURATION_EVALUATED_SEC)
    for _ in range(number_of_distributed_centralized_units)
]
for idx, cu in enumerate(cu_dus, start=1):
    dump_output_json(cu, os.path.join(output_path, f"distributed_centralized_unit_5g_{idx}.json"))

cores = [
    hardware_5g.CoreNetworkServer(duration_evaluated_sec=DURATION_EVALUATED_SEC)
    for _ in range(number_of_core_servers)
]
for idx, core in enumerate(cores, start=1):
    dump_output_json(core, os.path.join(output_path, f"core_network_server_5g_{idx}.json"))

switches = [
    generic_network_hardware.Switch(duration_evaluated_seconds=DURATION_EVALUATED_SEC)
    for _ in range(number_of_switches)
]
for idx, sw in enumerate(switches, start=1):
    dump_output_json(sw, os.path.join(output_path, f"switch_{idx}.json"))

network_5g = network_model_5g.Network5G(duration_evaluated_seconds=DURATION_EVALUATED_SEC,
                                        user_equipments=ues,
                                        radio_units=rus,
                                        distributed_centralized_units=cu_dus,
                                        core_network_servers=cores,
                                        switches=switches)

dump_output_json(network_5g, os.path.join(output_path, "network_5g.json"))

print("\nNETWORK")
print("----------------")
print("Total Network Energy Consumption (Wh): ", network_5g.total_energy_consumption_Wh)
