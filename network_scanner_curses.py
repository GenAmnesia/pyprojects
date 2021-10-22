#!/usr/bin python

import npyscreen
import subprocess
import argparse
import scapy.all as scapy


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Il range di ip da analizzare")
    parser.add_argument("-i", "--interface", dest="iface", help="L'interfaccia su cui eseguire lo scan")
    args = parser.parse_args()
    if not args.target:
        parser.error(
            "[-] Per favore specifica un range di ip da analizzare. Scrivi --help per ulteriori info.")
    if not args.iface:
        parser.error(
            "[-] Per favore specifica un'interfaccia da analizzare. Scrivi --help per ulteriori info.")
    return args


options = get_arguments()


def scan(ip, iface):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    clients_list = []
    answered_list = \
        scapy.srp(arp_request_broadcast, verbose=False, iface=iface, timeout=1, retry=3)[0]
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list


# print("Indirizzi MAC in ascolto su " + options.target)
def ipmac_gen():
    client_list = scan(options.target, options.iface)
    ips = []
    for client in client_list:
        ips.append(client["ip"])

    macs = []
    for client in client_list:
        macs.append(client["mac"])
    yield ips, macs
gen = ipmac_gen()
globalip, globalmac = list(next(gen))

def uimain():
    rows, colummns = subprocess.check_output(['stty', 'size']).split()
    centerx = (int(colummns) / 2)

    class App(npyscreen.NPSAppManaged):
        keypress_timeout_default = 100

        def onStart(self):
            npyscreen.setTheme(npyscreen.Themes.ElegantTheme)
            self.addForm("MAIN", MainForm, name="Network Scanner")
#           #Inizio Scan
            gen = ipmac_gen()
            self.ip_gen, self.mac_gen = list(next(gen))

        def while_waiting(self):
            try:
                ipmac_gen()
                gen = ipmac_gen()
                self.ip_gen, self.mac_gen = list(next(gen))

            except KeyboardInterrupt:
                message_to_display = 'In Uscita'
                npyscreen.notify_wait(message_to_display, title='Uscita')
                self.setNextForm(None)
                self.editing = False
                exit()


    class MainForm(npyscreen.Form):

        def while_waiting(self):
            #npyscreen.notify_wait("Sto aggiornando i dati...", title="Updating")
            self.desc.value = "In ascolto su " + options.target + " [Updating...]"
            self.ipre.values = self.parentApp.ip_gen
            self.macre.values = self.parentApp.mac_gen
            self.display()

        def create(self):
            key_of_choice = 'p'
            self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = self.spawn_exit_notify
            self.add_handlers({"^Q": self.spawn_exit_notify, key_of_choice: self.print_ips})
            self.desc = self.add(npyscreen.FixedText, value="In ascolto su " + options.target, editable=False)
            self.ipre = self.add(
                npyscreen.BoxTitle,
                name="Indirizzi IP",
                values=globalip,
                max_width=35, relx=(centerx - 35), rely=4,
                editable=False,
            )
            self.macre = self.add(
                npyscreen.BoxTitle,
                name="Indirizzi MAC",
                values=globalmac,
                max_width=35, relx=centerx, rely=4,
                editable=False
            )

        def print_ips(self, code_of_key_pressed):
            message_to_display = 'I popped up \n passed: {}'.format(code_of_key_pressed)
            npyscreen.notify_wait(message_to_display, title='Popup Title')
            print("IP STAMPATI!")

        def spawn_exit_notify(self, code_of_key_pressed):
            message_to_display = 'Uscita in corso...'.format(code_of_key_pressed)
            npyscreen.notify_wait(message_to_display, title='Uscita')
            exit()

        def exit_application(self):
            #self.parentApp.setNextForm(None)
            #self.editing = False
            pass


        def afterEditing(self):
            exit()

    if __name__ == "__main__":
        app = App().run()


try:
    uimain()
except KeyboardInterrupt:
    print("\n[+] In Uscita...")
