#!/usr/bin/env python3
import scapy.all as scapy
import optparse


def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target", dest="target", help="Il range di ip da analizzare")
    parser.add_option("-i", "--interface", dest="iface", help="L'interfaccia su cui eseguire lo scan")
    (options, arguments) = parser.parse_args()
    if not options.target:
        parser.error(
            "[-] Per favore specifica un range di ip da analizzare. Scrivi --help per ulteriori info.")
    if not options.iface:
        parser.error(
            "[-] Per favore specifica un'interfaccia da analizzare. Scrivi --help per ulteriori info.")
    return options





def scan(ip, iface):
    print("[+] Scanning on " + str(iface) + " for ip/range " + str(ip))
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, iface=iface, verbose=False, retry=3)[0]
    print("___________________________________________________________________")
    print("   IP \t\t\tAt MAC Address")
    print("-------------------------------------------------------------------")
    for element in answered_list:
        print(element[1].psrc + "\t\t" + element[1].hwsrc)


options = get_arguments()

scan(options.target, options.iface)
