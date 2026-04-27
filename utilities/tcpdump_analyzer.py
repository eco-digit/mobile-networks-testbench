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

import numpy as np
import datetime as dt
import os
import sys

class TcpDumpAnalyzer:
    def __init__(self, filename, clients_ips, servers_ips, decimals_packet_rate=1, decimals_interrival_times=3):
        self.source_tcdump_filename = filename
        self.local_ips = clients_ips
        self.remote_ips = servers_ips

        txt_file = self.open_txt_file()
        self.packets = self.get_packets(txt_file=txt_file)
        txt_file.close()
        self.capture_duration = self.get_capture_duration(self.packets)
        self.total_number_of_captured_packets = self.get_total_number_of_packets(self.packets)
        self.uplink_packets = self.get_uplink_packets(self.packets)
        self.number_of_uplink_packets = len(self.uplink_packets)
        self.downlink_packets = self.get_downlink_packets(self.packets)
        self.number_of_downlink_packets = len(self.downlink_packets)
        self.uplink_packet_size_bytes_distribution = self.get_packet_size_bytes_distribution(self.uplink_packets)
        self.downlink_packet_size_bytes_distribution = self.get_packet_size_bytes_distribution(self.downlink_packets)
        self.uplink_packet_rate_distribution = self.get_packet_rates_distribution(self.uplink_packets, decimals_packet_rate)
        self.downlink_packet_rate_distribution = self.get_packet_rates_distribution(self.downlink_packets, decimals_packet_rate)

    def open_txt_file(self):
      """
      Open the .txt file and read its contents.

      Returns
      -------
      file
          .txt file.
      """
      # Check if file exists
      if not os.path.exists(self.source_tcdump_filename):
        print(".txt file not found!")
        sys.exit(1)

      # Try to open file
      try:
        txt_file = open(self.source_tcdump_filename, 'r')
        return txt_file
      except:
        print("Error opening .txt file!")
        sys.exit(1)

    def get_packets(self, txt_file):
      """
      Get the timestamps and packets from the .txt file.

      Parameters
      ----------
      txt_file : file
          .txt file from tcpdump output.

      Returns
      -------
      list 
          Packets.

      """
      packets = []
      for line in txt_file:
        parts = line.strip().split()
        if len(parts) < 2:
          continue
        try:
          # Extract timestamp
          time_str = parts[0]
          time_obj = dt.datetime.strptime(time_str, "%H:%M:%S.%f")
          timestamp = time_obj
          
          # Extract packet data
          packet_data = ' '.join(parts[1:])
          packets.append((timestamp, packet_data))
        except ValueError:
          continue
      return packets
    
    def get_total_number_of_packets(self, packets):
      """
      Get the total number of packets in the .txt file.

      Returns
      -------
      int
          Total number of packets in the .txt file.
      """
      return len(packets)
    
    def get_packet_timestamp(self, packet):
      """
      Get the timestamp of the packet.

      Parameters
      ----------
      packet : tuple
          Packet tuple containing timestamp and packet data.

      Returns
      -------
      float
          Timestamp of the packet.
      """
      return packet[0]
    
    def get_packet_src_ip(self, packet):
      """
      Get the source IP of the packet.

      Parameters
      ----------
      packet : tuple
          Packet tuple containing timestamp and packet data.

      Returns
      -------
      str
          Source IP of the packet.
      """
      parts = packet[1].split()
      if len(parts) < 2 or parts[0] != "IP":
          return None
      # Extract the source IP address
      src_ip = parts[1].rsplit('.', 1)[0]
      return src_ip
    
    def get_packet_dst_ip(self, packet):
      """
      Get the destination IP of the packet.

      Parameters
      ----------
      packet : tuple
        Packet tuple containing timestamp and packet data.

      Returns
      -------
      str
        Destination IP of the packet.
      """
      parts = packet[1].split()
      if len(parts) < 4 or parts[0] != "IP" or '>' not in parts[2]:
          return None
      # Extract the destination IP address
      dst_ip = parts[3].rsplit('.', 1)[0]
      return dst_ip
    
    def get_packet_size(self, packet):
      """
      Get the size of the packet.

      Parameters
      ----------
      packet : tuple
        Packet tuple containing timestamp and packet data.

      Returns
      -------
      int
        Size of the packet.
      """
      parts = packet[1].split()
      if 'length' in parts:
        length_index = parts.index('length') + 1
        packet_size_str = parts[length_index].rstrip(':')  # Remove ':' if it exists
        packet_size = int(packet_size_str)
        return packet_size
      return None
    
    def get_capture_duration(self, packets):
      """
      Get the duration of the .txt file.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      float
          Duration of the .txt file in seconds.
      """
      if not packets:
          return 0.0
      return (self.get_packet_timestamp(packets[-1]) - self.get_packet_timestamp(packets[0])).total_seconds()
    
    def get_uplink_packets(self, packets):
      """
      Get the uplink packets from the .txt file.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      list
          uplink packets.
      """
      return [packet for packet in packets if self.get_packet_src_ip(packet) in self.local_ips]
    
    def get_downlink_packets(self, packets):
      """
      Get the downlink packets from the .txt file.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      list
          downlink packets.
      """
      return [packet for packet in packets if self.get_packet_dst_ip(packet) in self.local_ips]
    
    def get_packet_interarrival_times(self, packets):
      """
      Get the packet interarrival times.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      list
          Packet interarrival times.
      """
      return [self.get_packet_timestamp(packets[i+1]) - self.get_packet_timestamp(packets[i]) for i in range(len(packets)-1)]
    
    def get_mean_packet_interarrival_time(self, packets):
      """
      Get the mean packet interarrival time.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      float
          Mean packet interarrival time.
      """
      return np.mean([interarrival_time.total_seconds() for interarrival_time in self.get_packet_interarrival_times(packets)])
    
    def get_packet_sizes_bytes(self, packets):
      """
      Get the packet sizes in bytes.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      list
          Packet sizes in bytes.
      """
      return [self.get_packet_size(packet) for packet in packets]
    
    def get_packet_timestamps(self, packets):
      """
      Get the packet timestamps.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      list
          Packet timestamps.
      """
      return [self.get_packet_timestamp(packet) for packet in packets]
    
    def get_packet_size_bytes_distribution(self, packets):
      """
      Get the packet size probability.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      dict
          Packet size probability distribution.
      """
      packet_sizes = self.get_packet_sizes_bytes(packets)
      # remove None entries (packets without size)
      packet_sizes = [s for s in packet_sizes if s is not None]
      # return empty distribution if no sizes are available
      if not packet_sizes:
        return {}
      # sort the packet sizes
      packet_sizes.sort()
      packet_size_probability = {packet_size: packet_sizes.count(packet_size) / len(packet_sizes) for packet_size in packet_sizes}
      return packet_size_probability
    
    def get_packet_interarrival_time_distribution(self, packets, decimal_places=3):
      """
      Get the packet interarrival time probability.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      dict
          Packet interarrival time probability distribution.
      """
      packet_interarrival_times = [packet_interarrival_time.total_seconds() for packet_interarrival_time in self.get_packet_interarrival_times(packets)]
      # round the packet interarrival times
      packet_interarrival_times = [round(packet_interarrival_time, decimal_places) for packet_interarrival_time in packet_interarrival_times]
      # sort the packet interarrival times
      packet_interarrival_times.sort()
      packet_interarrival_time_probability = {packet_interarrival_time: packet_interarrival_times.count(packet_interarrival_time) / len(packet_interarrival_times) for packet_interarrival_time in packet_interarrival_times}
      return packet_interarrival_time_probability

    def get_packet_rates(self, packets):
      """
      Get the packet rates.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      list
          Packet rates.
      """

      packet_interarrival_times = self.get_packet_interarrival_times(packets)
      packet_rates = [1 / packet_interarrival_time.total_seconds() for packet_interarrival_time in packet_interarrival_times if packet_interarrival_time.total_seconds() != 0]
      return packet_rates
    
    def get_mean_packet_rate(self, packets):
      """
      Get the mean packet rate.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      float
          Mean packet rate.
      """
      return np.mean(self.get_packet_rates(packets))
    
    def get_packet_rates_distribution(self, packets, decimal_places=1):
      """
      Get the packet rate probability.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      dict
          Packet rate probability distribution.
      """
      packet_rates = self.get_packet_rates(packets)
      # round the packet rates
      packet_rates = [round(packet_rate, decimal_places) for packet_rate in packet_rates]
      # sort the packet rates
      packet_rates.sort()
      packet_rate_probability = {packet_rate: packet_rates.count(packet_rate) / len(packet_rates) for packet_rate in packet_rates if len(packet_rates) != 0}
      return packet_rate_probability
    