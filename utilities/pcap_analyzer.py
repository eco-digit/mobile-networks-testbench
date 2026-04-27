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

import dpkt
import numpy as np
import datetime as dt
import socket
import os
import sys

class PcapAnalyzer:
    def __init__(self, filename, clients_ips, servers_ips, decimals_packet_rate=1, decimals_interrival_times=3):
        self.filename = filename
        self.clients_ips = clients_ips
        self.servers_ips = servers_ips

        self.pcap_file = self.open_pcap_file()
        self.packets = self.get_pcap_packets()
        self.close_pcap_file()
        self.capture_duration = self.get_pcap_duration(self.packets)
        self.total_number_of_packets = self.get_total_number_of_packets(self.packets)
        self.uplink_packets = self.get_uplink_packets(self.packets)
        self.downlink_packets = self.get_downlink_packets(self.packets)
        self.mean_uplink_packet_rate = self.get_mean_packet_rate(self.uplink_packets)
        self.mean_downlink_packet_rate = self.get_mean_packet_rate(self.downlink_packets)
        self.uplink_packet_size_bytes_distribution = self.get_packet_size_bytes_distribution(self.uplink_packets)
        self.downlink_packet_size_bytes_distribution = self.get_packet_size_bytes_distribution(self.downlink_packets)
        self.uplink_packet_rate_distribution = self.get_packet_rates_distribution(self.uplink_packets, decimals_packet_rate)
        self.downlink_packet_rate_distribution = self.get_packet_rates_distribution(self.downlink_packets, decimals_packet_rate)

    def open_pcap_file(self):
      """
      Open the .pcap file and read its contents.

      Returns
      -------
      file
          .pcap file.
      """
      # Check if file exists
      if not os.path.exists(self.filename):
        print(".pcap file not found!")
        sys.exit(1)

      # Try to open file
      try:
        pcap_file = open(self.filename, 'rb')
        return pcap_file
      except:
        print("Error opening .pcap file!")
        sys.exit(1)

    def get_pcap_packets(self):
      """
      Get the timestamps and packets from the .pcap file.

      Returns
      -------
      list 
          Packets.

      """
      pcap = dpkt.pcap.Reader(self.pcap_file)
      packets = [(ts, pkt) for ts, pkt in pcap]
      return packets
    
    def get_total_number_of_packets(self, packets):
      """
      Get the total number of packets in the .pcap file.

      Returns
      -------
      int
          Total number of packets in the .pcap file.
      """
      return len(packets)
    
    def get_packet_timestamp(self, packet):
      """
      Get the timestamp of the packet.

      Parameters
      ----------
      packet : dpkt.pcap.Packet
          Packet.

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
      packet : dpkt.pcap.Packet
          Packet.

      Returns
      -------
      str
          Source IP of the packet.
      """
      eth = dpkt.ethernet.Ethernet(packet[1])
      if (isinstance(eth.data, dpkt.ip.IP) or isinstance(eth.data, dpkt.ip6.IP6)):
        # Grab the data within the Ethernet frame (the IP packet)
        ip = eth.data
        
        # Source
        # Try IPv4 and IPv6 format
        try:
          src_ip = socket.inet_ntop(socket.AF_INET, ip.src)
          return src_ip
        except ValueError:
          try:
            src_ip = socket.inet_ntop(socket.AF_INET6, ip.src)
            return src_ip
          except ValueError:
            return None
    
    def get_packet_dst_ip(self, packet):
      """
      Get the destination IP of the packet.

      Parameters
      ----------
      packet : dpkt.pcap.Packet
          Packet.

      Returns
      -------
      str
          Destination IP of the packet.
      """
      eth = dpkt.ethernet.Ethernet(packet[1])
      if (isinstance(eth.data, dpkt.ip.IP) or isinstance(eth.data, dpkt.ip6.IP6)):
        # Grab the data within the Ethernet frame (the IP packet)
        ip = eth.data
        
        # Destination
        # Try IPv4 and IPv6 format
        try:
          dst_ip = socket.inet_ntop(socket.AF_INET, ip.dst)
          return dst_ip
        except ValueError:
          try:
            dst_ip = socket.inet_ntop(socket.AF_INET6, ip.dst)
            return dst_ip
          except ValueError:
            return None
    
    def get_packet_size(self, packet):
      """
      Get the size of the packet.

      Parameters
      ----------
      packet : dpkt.pcap.Packet
          Packet.

      Returns
      -------
      int
          Size of the packet.
      """
      return len(packet[1])
    
    def get_pcap_duration(self, packets):
      """
      Get the duration of the .pcap file.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      float
          Duration of the .pcap file.
      """
      return self.get_packet_timestamp(packets[-1]) - self.get_packet_timestamp(packets[0])
    
    def get_uplink_packets(self, packets):
      """
      Get the uplink packets from the .pcap file.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      list
          uplink packets.
      """
      return [packet for packet in packets if self.get_packet_src_ip(packet) in self.clients_ips]
    
    def get_downlink_packets(self, packets):
      """
      Get the downlink packets from the .pcap file.

      Parameters
      ----------
      packets : list
          Packets.

      Returns
      -------
      list
          downlink packets.
      """
      return [packet for packet in packets if self.get_packet_dst_ip(packet) in self.clients_ips]
    
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
      return np.mean(self.get_packet_interarrival_times(packets))
    
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
      packet_interarrival_times = self.get_packet_interarrival_times(packets)
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
      packet_rates = [1 / packet_interarrival_time for packet_interarrival_time in packet_interarrival_times if packet_interarrival_time != 0]
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

    
    def close_pcap_file(self):
      """
      Close the .pcap file.
      """
      self.pcap_file.close()
    