# Mobile Networks Testbench

Power and energy consumption estimation for (5G) mobile networks.

## Overview

This tool estimates the power and energy consumption of a given mobile network. First, the network is defined in terms of the deployed hardware components (radio units, servers for the 5G core etc.).
Then, the radio resource utilization (load) of the network is estimated based on given the data traffic.
Based on the load, the power consumption and energy consumption of the individual network components and the whole network are estimated.

## Getting Started

This section gives an introduction to the necessary prerequisites to get started with this project.

### Requirements

A Python installation is required to run the project files.

Links to Python downloads for various operating systems and further guides on installing and setting up Python can be found at:
[wiki.python.org/moin/BeginnersGuide/Download](https://wiki.python.org/moin/BeginnersGuide/Download)

Tested with Python 3.12.0.
(However, any Python version 3.x.x should work.)

The installed Python version can be verified by running the following command in the terminal/CLI of your operating system:

```bash
python --version
```

Additionally, certain Python packages (not included in the standard Python installation) are required. Installation procedure for these packages is explained in the following section.

### Install

The required Python packages may be installed using the package installer [pip](https://pypi.org/project/pip/) with the following command:

```bash
pip install -r requirements.txt
```

If this command fails due to a missing pip installation, check wether pip is installed along with your Python installation with the following command:

```bash
python -m pip --version
```

Depending on how Python was installed, these packages may already be installed. The packages listed in [requirements.txt](requirements.txt) can also be installed individually using your preferred Python packet manager.

Also check the [guide](https://packaging.python.org/en/latest/tutorials/installing-packages/) in case of issues with the installation. Optionally, the packages can be installed in a virtual environment - this is also described in the guide.

### Usage

The library can be used with a simple CLI. Running [main.py](main.py) with two arguments will yield the calculated results of the models.

The input configuration and parameters are provided with two files: 

1) An input JSON file
2) A template JSON file

The input JSON file can be located anywhere, the file path needs to be provided as the first argument when running [main.py](main.py). 

The templates are located in the folder [templates](templates). The path to the template file is defined in the input JSON file.

Furthermore, an output directory needs to be provided as the second argument when running the testbench.
The results will be written as multiple JSON files to the given output directory.

An example CLI input to run the testbench is given below:

```bash
python main.py input_example.json output_folder/
```

## Structure of the input JSON

The input JSON file provides the basic mode of configuring and defining the parameters for the testbench.

It includes the "technology" parameter (currently only "5G" is supported), the "template" parameter (name of the template) and the load profile ("loadProfile"). 

There are three options to define the load profile:
1) Packet capture (PCAP)
2) Distribution of packet sizes and packet rate ("manual input")
3) tcpdump summary text file

To specify if a PCAP or manually entered distributions or the tcpdump summary should be used, the key "mode" needs to set to either "pcap" or "distribution" or "tcpdump". It is not possible to combine the options.

The load profile can be defined based on a PCAP file (packet capture). The parameter "pcapFile" provides the location of the PCAP file to be analyzed (relative to main.py). The source and destination IP adresses must be provided as a list. A packet sent from a client to a server adress is interpreted as being sent by a user (UE) over the 5G network in uplink direction. A packet received by a server IP address and sent by a client address is interpreted as a downlink packet.
It is important to note that the packets must be saved in the PCAP with their full payload, as the dpkt library cannot extract the correct packet size otherwise.

Alternatively, the load profile can be manually specified with distributions. The packet sizes in uplink and downlink as well as the packet rates in uplink and downlink need to be specified. Multiple values can be given in a list. For each value, a probability must be given in the corresponding list.

The third option is to provide a tcpdump summary text file that contains the IP address source and destination as well as the packet length. Each frame is given in the following format:

```
09:25:17.267882 IP 172.19.0.3.40068 > 172.19.0.2.http: Flags [.], ack 983311, win 14975, options [nop,nop,TS val 4033629268 ecr 1503341387], length 0
```

The repository contains an example capture.txt file that was captured with tcpdump.
A list of client and server addresses must be given for the tcpdump option. They are interpreted in the same way as for the pcap option. 

The number of UEs per cell of the network can be defined, this will multiply the traffic by the number of UEs for the load calculation per cell.
Finally, the duration in seconds that should be evaluated for the energy consumption calculation must be specified for this mode of input as well. 

An example input JSON is provided below, showing the two modes of specifying the load profile:

```json
{
    "technology": "5G",
    "template": "templates/nr_5g/template_campus_siemens_draft.json",
    "loadProfile" : {
        "numberUserEquipmentsPerCell": 2,
        "trafficInputMode": "pcap",
        "pcap": {
            "pcapFile" : "sample1.pcap",
            "pcapIPClients": ["192.168.178.41"],
            "pcapIPServers": ["52.98.240.130"]
        },
        "tcpdump": {
            "tcpdumpFile" : "capture.txt",
            "tcpdumpIPClients": ["172.19.0.3"],
            "tcpdumpIPServers": ["172.19.0.2"]
        },
        "distribution": {
            "packetSizeUplink_bytes": [1500, 300],
            "packetSizeDownlink_bytes": [1500, 300],
            "packetSizeUplinkProbability": [0.5, 0.5],
            "packetSizeDownlinkProbability": [0.5, 0.5],
            "packetRateUplink_packets_per_second": [8000, 2000],
            "packetRateDownlink_packets_per_second": [8000, 4000],
            "packetRateUplinkProbability": [0.5, 0.5],
            "packetRateDownlinkProbability": [0.5, 0.5],
            "durationEvaluated_sec": 3600
        }
        
    }
}
```

### Input JSON Parameters

#### Global Parameters
- `technology`: Technology standard (currently "5G")
- `template`: Path to the template JSON file defining the network infrastructure

#### Load Profile Parameters
- `numberUserEquipmentsPerCell`: Number of user equipment devices per cell (multiplies traffic)
- `trafficInputMode`: Method for specifying traffic - options are "pcap", "tcpdump", or "distribution"

#### PCAP Mode Parameters
- `pcap.pcapFile`: Path to the PCAP file containing packet capture data
- `pcap.pcapIPClients`: List of client IP addresses (UE/uplink source)
- `pcap.pcapIPServers`: List of server IP addresses (downlink source)

#### Tcpdump Mode Parameters
- `tcpdump.tcpdumpFile`: Path to tcpdump summary text file
- `tcpdump.tcpdumpIPClients`: List of client IP addresses (UE/uplink source)
- `tcpdump.tcpdumpIPServers`: List of server IP addresses (downlink source)

#### Distribution Mode Parameters
- `distribution.packetSizeUplink_bytes`: List of possible uplink packet sizes in bytes
- `distribution.packetSizeDownlink_bytes`: List of possible downlink packet sizes in bytes
- `distribution.packetSizeUplinkProbability`: List of probabilities for each uplink packet size
- `distribution.packetSizeDownlinkProbability`: List of probabilities for each downlink packet size
- `distribution.packetRateUplink_packets_per_second`: List of possible uplink packet rates
- `distribution.packetRateDownlink_packets_per_second`: List of possible downlink packet rates
- `distribution.packetRateUplinkProbability`: List of probabilities for each uplink packet rate
- `distribution.packetRateDownlinkProbability`: List of probabilities for each downlink packet rate
- `distribution.durationEvaluated_sec`: Duration in seconds to evaluate for energy consumption

## Structure of the template JSON

Modifying the parameters in the template JSON is intended for advanced users of the testbench. The given template JSON in [template_campus_siemens_draft.json](templates/nr_5g/template_campus_siemens_draft.json) contains parameters for a generic examüple network.

### Template JSON Parameters

```json
{
    "_comment": "all settings here are set for the template with default values, available params can vary per template",
    "technology": "5G",
    "templateName": "5G Campus Draft",
    "radioResourceParameters": {
        "slotDuration_ms": 1,
        "availablePRBs": 273,
        "modulationOrder": 6,
        "codingRate": 0.75,
        "mimoLayersUplink": 4,
        "mimoLayersDownlink": 4,
        "beamsMUMIMO": 1,
        "scalingFactorUplink": 1,
        "scalingFactorDownlink": 1,
        "numberOfAggregatedCarriers": 1,
        "symbolsPerSlot": 14,
        "overheadFraction": 0.15,
        "subcarriersPerPRB": 12,
        "partSlotsDownlink": 0.75,
        "partSlotsUplink": 0.2
    },
    "networkParameters": {
        "numberRadioUnits": 1,
        "numberDistributedCentralizedUnits": 1,
        "numberCoreServers": 1,
        "numberSwitches": 1,
        "cellsPerRadioUnit": 1
    }
}
```

#### Global Parameters
- `_comment`: Documentation field for template settings and available parameters
- `technology`: Technology standard (currently "5G")
- `templateName`: Human-readable name for the template

#### Radio Resource Parameters
Radio resource parameters define the physical layer characteristics of the 5G network:

- `slotDuration_ms`: Duration of each transmission slot in milliseconds
- `availablePRBs`: Number of Physical Resource Blocks available
- `modulationOrder`: Modulation scheme order (affects data rate)
- `codingRate`: Channel coding rate (0-1), affects data throughput
- `mimoLayersUplink`: Number of MIMO layers for uplink transmission
- `mimoLayersDownlink`: Number of MIMO layers for downlink transmission
- `beamsMUMIMO`: Number of beams for multi-user MIMO
- `scalingFactorUplink`: Power scaling factor for uplink
- `scalingFactorDownlink`: Power scaling factor for downlink
- `numberOfAggregatedCarriers`: Number of aggregated carriers for increased bandwidth
- `symbolsPerSlot`: Number of OFDM symbols per slot
- `overheadFraction`: Fraction of resources used for overhead (control signaling)
- `subcarriersPerPRB`: Number of subcarriers per Physical Resource Block
- `partSlotsDownlink`: Fraction of slots dedicated to downlink transmission
- `partSlotsUplink`: Fraction of slots dedicated to uplink transmission

#### Network Parameters
Network parameters define the hardware infrastructure of the deployed network:

- `numberRadioUnits`: Number of radio access units (base stations, gNodeBs)
- `numberDistributedCentralizedUnits`: Number of distributed/centralized processing units
- `numberCoreServers`: Number of servers in the 5G core network
- `numberSwitches`: Number of network switches for interconnection
- `cellsPerRadioUnit`: Number of cells served by each radio unit

## Structure of the results

The results are written to JSON files in the given output directory (CLI argument).

The results are divided into per node results (one file for user equipment, radio unit...) and network level results (one file).

## Copyright Notice

Copyright Siemens AG, 2023-2026. Part of the ECO:DIGIT Project.

