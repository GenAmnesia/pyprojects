#!/bin/env/ python
import subprocess
import optparse
import re


def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface to change its MAC address")
    parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address")
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please specify an interface, use --help for info.")
    elif not options.new_mac:
        parser.error("[-] Please specify a new MAC address, use --help for info.")
    return options


def change_mac(i, m):
    print("[+] Changing MAC Address for " + i + " to " + m)
    subprocess.call(['ifconfig', i, 'down'])
    subprocess.call(['ifconfig', i, 'hw', 'ether', m])
    subprocess.call(['ifconfig', i, 'up'])


def get_current_mac(i):
    ifconfig = subprocess.check_output(['ifconfig', i])
    curr_mac = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig))
    if curr_mac:
        return curr_mac.group(0)
    else:
        print("[-] Could not read the MAC address.")


options = get_arguments()

current_mac = get_current_mac(options.interface)
print("Current MAC = " + str(current_mac))

change_mac(options.interface, options.new_mac)

current_mac = get_current_mac(options.interface)
if current_mac == options.new_mac:
    print("[+] MAC Address successfully changed to " + current_mac)
else:
    print("[-] Error. MAC Address not changed.")
