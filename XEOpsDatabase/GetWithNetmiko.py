"""Helper class which collect and call to database for writing"""

import collections
import XEOpsDatabase.connection as ConnectWith
import XEOpsDatabase.DbOperations as DbOps
from netmiko import ssh_exception
import time
import ipaddress


class PollWithNetmiko:
    """Polling with Netmiko"""

    def __init__(self):

        self.device = None
        self.username = None
        self.password = None
        self.ssh_port = 22
        self.session = None

        # Calling polling method
        self.start_polling()

    def start_polling(self):
        """Endless loop for device polling"""
        while True:
            # Query facts table in DB and get host IP
            for i in DbOps.session.query(DbOps.DeviceFacts).all():
                # Gets host credentials and IP
                self.username = i.username
                self.password = i.password
                self.device = i.unique_id
                # Creats session with DB row attributes
                self.session = ConnectWith.creat_netmiko_connection(self.username, self.password, self.device,
                                                                    self.ssh_port)
                # Call methods which collects data from device
                self.get_vlans()
                self.get_arp()
                self.get_mac_arp_table()
                self.get_span_root()
                self.get_cdp_neighbors()
                self.get_ospf_status()
                self.get_bgp_status()
                self.get_vrfs()
                self.get_ospf_processes()
                self.get_access_ports()

                # Sleep before next poll
                time.sleep(10)

    def send_command(self, command, expect_string=None):
        """Send Netmiko commands"""

        get_response = None

        if expect_string is None:

            retries = 0
            while retries != 3:
                try:
                    get_response = self.session.send_command(command)
                    break
                except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException):
                    self.session = ConnectWith.creat_netmiko_connection(self.username, self.password, self.device,
                                                                        self.ssh_port)
                    retries += 1

        else:

            retries = 0
            while retries != 3:
                try:
                    get_response = self.session.send_command(command, expect_string=expect_string)
                    break
                except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException):
                    self.session = ConnectWith.creat_netmiko_connection(self.username, self.password, self.device,
                                                                        self.ssh_port)

                    retries += 1

        if retries == 3:
            get_response = 'Error Connecting'

        return get_response

    def get_model(self):
        """Get self.device model"""

        model = None
        show_inventory = self.send_command('show inventory')

        for i in show_inventory.splitlines():
            if i.rfind('Chassis') != -1:
                model = i.split("\"")[3].split()[1][0:3]

        return model

    def get_vrfs(self):
        """Get self.device model"""

        vrfs = []
        get_vrf = self.send_command('show vrf')

        for i in get_vrf.splitlines():
            try:
                if i.rfind('Name') == -1:
                    vrfs.append(i.split()[0])
            except IndexError:
                pass

        return vrfs

    def get_bgp_status(self):
        """Gets BGF neighbor statuses"""

        local_as = ['Null']
        bgp_summary = self.send_command('show ip bgp summary')

        for i in bgp_summary.splitlines():
            if i.rfind('local AS number') != -1:
                local_as = i.split()[-1:]
            try:
                ipaddress.ip_address(i.split()[0])
                DbOps.update_bgp_table(self.device, i.split()[0], i.split()[2], i.split()[8], i.split()[9], local_as)
            except (ValueError, IndexError):
                pass

    def get_ospf_status(self):
        """Gets OSPF neighbor statuses"""

        neighbor_status = collections.defaultdict(list)
        ospf_summary = self.send_command('show ip ospf neighbor')

        if ospf_summary:
            for i in ospf_summary.splitlines():
                try:
                    neighbor = ipaddress.ip_address(i.split()[0])
                    neighbor_status[neighbor].append(
                        {"NeighborID": i.split()[0], 'State': i.split()[2].strip("/"), 'Address': i.split()[5],
                         'Interface': i.split()[6]})
                except (ValueError, IndexError):
                    pass
        else:
            ip_ospf = self.send_command('show ip ospf')
            if ip_ospf:
                neighbor_status['neighbor'].append(
                    {"NeighborID": 'No Established Neighbors', 'State': 'None', 'Address': 'None', 'Interface': 'None'})
            else:
                neighbor_status = []

        if neighbor_status:
            for k, v in neighbor_status.items():
                for i in v:
                    DbOps.update_ospf_table(self.device, i['NeighborID'], i['State'], i['Address'],
                                            i['Interface'])

    def get_ospf_processes(self):
        """Get OSPF processes"""

        ospf_process = self.send_command('show ip ospf | i Process')
        if ospf_process:
            for process in ospf_process.splitlines():
                try:
                    DbOps.update_ospf_process_table(self.device, process.split('"')[1].split()[1])
                except IndexError:
                    continue

    def get_arp(self):
        """Get ARP table"""

        arps = []
        get_arps = self.send_command('show ip arp')

        if get_arps:
            for i in get_arps.splitlines():
                try:
                    if i.split()[0] != 'Protocol':
                        arps.append(
                            {"Protocol": i.split()[0], 'Address': i.split()[1], 'Age': i.split()[2],
                             'MAC': i.split()[3], 'Type': i.split()[4], 'Interfaces': i.split()[5]})
                except IndexError:
                    pass
        else:
            return 'An Error Occured'

        for i in arps:
            DbOps.update_arp_table(self.device, i['Protocol'], i['Address'], i['Age'], i['MAC'], i['Type'],
                                   i['Interfaces'])

    def get_cdp_neighbors(self):
        """Gets mac and arp tables. Concatinates into one"""

        get_cdp_neigh = 'show cdp neighbors'
        name = None
        local_port = None
        remote_port = None

        # Gets and parse mac table response
        cdp_neighbors = self.send_command(get_cdp_neigh)
        for neighbor in cdp_neighbors.splitlines():
            try:
                if not neighbor:
                    continue
                elif neighbor.split()[0] == "":
                    continue
                elif neighbor.split()[0] == 'Capability':
                    continue
                elif neighbor.split()[0] == 'Device':
                    continue
                if len(neighbor.split()) == 1:
                    name = neighbor.split()[0]
                elif len(neighbor.split()) == 7:
                    remote_port = neighbor.split()[5] + neighbor.split()[6]
                    local_port = neighbor.split()[0] + neighbor.split()[1]
                elif len(neighbor.split()) == 8:
                    remote_port = neighbor.split()[6] + neighbor.split()[7]
                    local_port = neighbor.split()[0] + neighbor.split()[1]
                elif len(neighbor.split()) == 9:
                    remote_port = neighbor.split()[7] + neighbor.split()[8]
                    local_port = neighbor.split()[0] + neighbor.split()[1]

            except IndexError:
                continue

            if remote_port is not None:
                DbOps.update_cdp_table(self.device, name, local_port, remote_port)

    def get_span_root(self):
        """Gets mac and arp tables. Concatinates into one"""

        span_table = []
        get_macs = 'show spanning-tree root'

        # Gets and parse mac table response
        table = self.send_command(get_macs)

        for vlan in table.splitlines():
            try:
                if vlan.split()[0].rfind("-") != -1:
                    continue
                elif vlan.split()[0] == 'Vlan':
                    continue
                else:
                    if vlan.split()[0][-2] == "0":

                        if len(vlan.split()) == 8:
                            span_table.append(
                                {'vlan': vlan.split()[0].strip('VLAN'), 'root-prio': vlan.split()[1],
                                 'root-id': vlan.split()[2],
                                 'root-cost': vlan.split()[3], 'root-port': vlan.split()[7]})
                        elif len(vlan.split()) == 7:
                            span_table.append(
                                {'vlan': vlan.split()[0].strip('VLAN'), 'root-prio': vlan.split()[1],
                                 'root-id': vlan.split()[2],
                                 'root-cost': vlan.split()[3], 'root-port': "Root Bridge"})
                    else:

                        if len(vlan.split()) == 8:
                            span_table.append(
                                {'vlan': vlan.split()[0].strip('VLAN'), 'root-prio': vlan.split()[1],
                                 'root-id': vlan.split()[2],
                                 'root-cost': vlan.split()[3], 'root-port': vlan.split()[7]})
                        elif len(vlan.split()) == 7:
                            span_table.append(
                                {'vlan': vlan.split()[0].strip('VLAN'), 'root-prio': vlan.split()[1],
                                 'root-id': vlan.split()[2],
                                 'root-cost': vlan.split()[3], 'root-port': "Root Bridge"})
            except IndexError:
                continue

        for i in span_table:
            DbOps.update_spann_tree_table(self.device, i['vlan'], i['root-prio'], i['root-id'],
                                          i['root-cost'],
                                          i['root-port'])

    def get_mac_arp_table(self):
        """Gets mac and arp tables. Concatinates into one"""

        mac_table = []
        arp_table = []

        get_macs = 'show mac address-table'
        gets_arps = 'show ip arp'

        # Gets and parse mac table response
        table = self.send_command(get_macs)
        for mac in table.splitlines():
            try:
                if mac.split()[0].rfind("-") != -1:
                    continue
                elif mac.split()[0] == 'Vlan':
                    continue
                elif mac.split()[0] == 'All':
                    continue
                elif mac.split()[0] == 'Total':
                    continue
                elif mac.split()[0] == '%':
                    break
                else:
                    mac_table.append({'vlan': mac.split()[0], 'address': mac.split()[1], 'type': mac.split()[2],
                                      'interface': mac.split()[3]})
            except IndexError:
                continue

        # Gets and parse arp table response
        arps = self.send_command(gets_arps)
        for arp in arps.splitlines():
            try:
                if arp.split()[0] == 'Protocol':
                    continue
                elif arp.split()[0] == 'Total':
                    continue
                elif arp.split()[0] == '%':
                    break
                else:
                    arp_table.append(
                        {'protocol': arp.split()[0], 'ip': arp.split()[1], 'age': arp.split()[2], 'mac': arp.split()[3],
                         'interface': arp.split()[5]})
            except IndexError:
                continue

        # Check to see if mac has an arp entry. If so, add k/v to existing dictionary
        for mac in mac_table:
            for entry in arp_table:
                if mac.get('address') == entry.get('mac'):
                    mac['ip'] = entry.get('ip')
                    mac['ip_int'] = entry.get('interface')
                    break
                else:
                    mac['ip'] = 'None'
                    mac['ip_int'] = 'None'

        if mac_table:
            for i in mac_table:
                DbOps.update_mac_arp_table(self.device, i['vlan'], i['address'], i['type'], i['interface'],
                                           i['ip'], i['ip_int'])

    def get_access_ports(self):
        """Get trunks"""

        interface_command = 'show interfaces status'

        get_interfaces = self.send_command(interface_command)

        cli_line = get_interfaces.split("\n")
        for line in cli_line:
            if not list(enumerate(line.split(), 0)):
                continue
            if line.split()[0] == "Port":
                continue
            else:
                if len(line.split()) == 6:
                    DbOps.update_access_interfaces_table(self.device, line.split()[0], line.split()[2], line.split()[1],
                                                         line.split()[3], line.split()[4], line.split()[5])
                elif len(line.split()) == 6:
                    print(line.split())
                    DbOps.update_access_interfaces_table(self.device, line.split()[0], line.split()[2], line.split()[1],
                                                         line.split()[3], line.split()[4], 'None')

    def get_vlans(self):
        """Get vlans"""

        iter_vlan = "1"
        get_vlans = 'show vlan brief'
        get_vlan_pro = 'show spanning-tree bridge priority'
        vlan_ports = None

        vlans = self.send_command(get_vlans)
        get_prio = self.send_command(get_vlan_pro)

        for vlan in vlans.splitlines():
            try:
                if not vlan:
                    continue
                if not (enumerate(vlan.split(), 0)):
                    continue
                elif vlan.split()[0] == "":
                    continue
                elif vlan.split()[0].rfind("VLAN") != -1:
                    continue
                elif vlan.split()[0].rfind("-") != -1:
                    continue
                if iter_vlan != vlan.split()[0] or iter_vlan == "1":
                    if vlan.split()[0].rfind("/") != -1:
                        vlan_ports = ' '.join(vlan.split())
                    else:
                        vlan_ports = ' '.join(vlan.split()[3:])

                for prio in get_prio.splitlines():
                    try:
                        if list(enumerate(prio.split(), 0))[0][1][-2:] == list(enumerate(vlan.split(), 0))[0][1]:
                            DbOps.update_vlan_table(self.device, prio.split()[0][-2:], prio.split()[1],
                                                    vlan.split()[1], vlan.split()[2], vlan_ports)

                    except IndexError:
                        pass

                iter_vlan = vlan.split()[0]

            except IndexError:
                pass
