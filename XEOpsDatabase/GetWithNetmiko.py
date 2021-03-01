"""Helper class which collect and call to database for writing"""

import connection as ConnectWith
import DbOperations as DbOps
from netmiko import ssh_exception
import ipaddress


def netconf_trunk_helper(interface, username, password, device):
    """Get route-map names"""

    session = ConnectWith.creat_netmiko_connection(username, password, device, 22)

    vlans = []
    int_trunk_command = f'show run interface {interface} | i allowed vlan'
    get_int_trunk = send_command(int_trunk_command, session)

    for line in get_int_trunk.splitlines():
        if not list(enumerate(line.split(), 0)):
            continue
        elif line.split()[0] == '^':
            break
        elif len(line.split()) == 5:
            vlans.append(line.split()[4])
        elif len(line.split()) == 6:
            vlans.append(line.split()[5])

    return vlans


def get_dmvpn_interface(session, interface, device):
    """Get route-map names"""

    ip_add, tunnel_source, tunnel_mode, network_id, holdtime, profile, nhrp_shortcut, nhrp_red = None, None, None, None, \
                                                                                                 None, None, None, None

    DbOps.delete_rows('dmvpninterfaces_back_end', device)

    try:
        for line in send_command(f'show run interface {interface} | ex Current|Building|!', session).splitlines():
            if len(line.split()) == 0:
                continue
            elif '^' == line.split()[0]:
                break
            elif 'network-id' in line:
                network_id = line.split()[3]
            elif 'interface' in line:
                pass
            elif 'address' in line:
                ip_add = f'{line.split()[2]} {line.split()[3]}'
            elif 'source' in line:
                tunnel_source = line.split()[2]
            elif 'mode' in line:
                tunnel_mode = f'{line.split()[2]} {line.split()[3]}'
            elif 'protection' in line:
                profile = line.split()[4]
                DbOps.update_dmvpn_interfaces(device, interface, ip_add, tunnel_source, tunnel_mode, network_id,
                                              holdtime, profile, nhrp_shortcut, nhrp_red)
            elif 'holdtime' in line:
                holdtime = line.split()[3]

            # Check dmvpn phase commands
            if 'shortcut' in line:
                nhrp_shortcut = line.split()[2]
            if 'nhrp redirect' in line:
                nhrp_red = line.split()[2]

    except AttributeError:
        pass


def send_command(command, session):
    """Send Netmiko commands"""

    get_response = None

    retries = 0
    while retries != 3:
        try:
            get_response = session.send_command(command)
            break
        except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException, EOFError):
            retries += 1

    if retries == 3:
        get_response = 'Error Connecting'

    return get_response


class PollWithNetmiko:
    """Polling with Netmiko"""

    def __init__(self, device, username, password, ssh_port, model, netconf_port):

        self.device = device
        self.username = username
        self.password = password
        self.ssh_port = ssh_port
        self.netconf_port = netconf_port
        self.model = model
        self.session = None

        # Calling polling method
        self.start_polling()

    def start_polling(self):
        """Endless loop for device polling"""

        self.session = ConnectWith.creat_netmiko_connection(self.username, self.password, self.device,
                                                            self.ssh_port)

        # Check for device type. Insures polling only happens with compatable technologies
        if self.model[:3][-2:] != 'SR':
            self._get_vlans()
            self._get_mac_arp_table()
            self._get_access_ports()
            self._get_span_root()

        elif self.model[:3][-2:] == 'SR':
            self._get_dmvpn()
            self._get_dmvpn_info()

        self._get_arp()
        self._get_cdp_neighbors()
        self._get_ospf_status()
        self._get_bgp_status()
        self._get_vrfs()
        self._get_ospf_processes()
        self._get_route_maps()
        self._get_hsrp_status()
        self._get_ospf_routers()
        self._gather_facts()

        DbOps.copy_db_table(self.device)

    def send_command(self, command, expect_string=None):
        """Send Netmiko commands"""

        get_response = None

        try:
            get_response = self.session.send_command(command, expect_string=expect_string)
        except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException, EOFError):
            pass

        return get_response

    def get_model(self):
        """Get self.device model"""

        model = None

        try:
            for i in self.send_command('show inventory').splitlines():
                if i.rfind('Chassis') != -1:
                    model = i.split("\"")[3].split()[1][0:3]
        except AttributeError:
            pass

        return model

    def _get_vrfs(self):
        """Get self.device model"""

        # Delete table data
        DbOps.delete_rows('vrfs_back_end', self.device)

        try:
            for i in self.send_command('show vrf').splitlines():
                try:
                    if i.rfind('Name') == -1:
                        DbOps.update_vrfs_table(self.device, i.split()[0])
                except IndexError:
                    pass
        except AttributeError:
            pass

    def _get_bgp_status(self):
        """Gets BGF neighbor statuses"""

        local_as = ['Null']

        # Delete table data
        DbOps.delete_rows('bgp_back_end', self.device)

        try:
            for i in self.send_command('show ip bgp summary').splitlines():
                if i.rfind('local AS number') != -1:
                    local_as = i.split()[-1:]
                try:
                    ipaddress.ip_address(i.split()[0])
                    DbOps.update_bgp_table(self.device, i.split()[0], i.split()[2], i.split()[8], i.split()[9],
                                           local_as)
                except (ValueError, IndexError):
                    pass
        except AttributeError:
            pass

    def _get_ospf_status(self):
        """Gets OSPF neighbor statuses"""

        # Delete table data
        DbOps.delete_rows('ospf_back_end', self.device)

        try:
            if self.send_command('show ip ospf neighbor').splitlines():
                for i in self.send_command('show ip ospf neighbor').splitlines():
                    try:
                        ipaddress.ip_address(i.split()[0])
                        DbOps.update_ospf_table(self.device, i.split()[0], i.split()[2].strip("/"), i.split()[5],
                                                i.split()[6])
                    except (ValueError, IndexError):
                        pass
            else:
                if self.send_command('show ip ospf').splitlines():
                    DbOps.update_ospf_table(self.device, 'No Established Neighbors', 'None', 'None', 'None')
        except AttributeError:
            pass

    def _get_ospf_processes(self):
        """Get OSPF processes"""

        # Delete table data
        DbOps.delete_rows('ospfprocess_back_end', self.device)

        try:
            if self.send_command('show ip ospf | i Process'):
                for process in self.send_command('show ip ospf | i Process').splitlines():
                    try:
                        DbOps.update_ospf_process_table(self.device, process.split('"')[1].split()[1])
                    except IndexError:
                        continue
        except AttributeError:
            pass

    def _get_arp(self):
        """Get ARP table"""

        # Delete table data
        DbOps.delete_rows('arp_back_end', self.device)

        try:
            for i in self.send_command('show ip arp').splitlines():
                try:
                    if i.split()[0] != 'Protocol':
                        DbOps.update_arp_table(self.device, i.split()[0], i.split()[1], i.split()[2], i.split()[3],
                                               i.split()[4],
                                               i.split()[5])
                except IndexError:
                    pass
        except AttributeError:
            pass

    def _get_cdp_neighbors(self):
        """Gets mac and arp tables. Concatinates into one"""

        name = None

        # Delete table data
        DbOps.delete_rows('cdp_back_end', self.device)

        try:
            for neighbor in self.send_command('show cdp neighbors').splitlines():
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
                        DbOps.update_cdp_table(self.device, name, local_port, remote_port)
                        continue
                    elif len(neighbor.split()) == 8:
                        remote_port = neighbor.split()[6] + neighbor.split()[7]
                        local_port = neighbor.split()[0] + neighbor.split()[1]
                        DbOps.update_cdp_table(self.device, name, local_port, remote_port)
                        continue
                    elif len(neighbor.split()) == 9:
                        remote_port = neighbor.split()[7] + neighbor.split()[8]
                        local_port = neighbor.split()[0] + neighbor.split()[1]
                        DbOps.update_cdp_table(self.device, name, local_port, remote_port)
                        continue

                except IndexError:
                    continue
        except AttributeError:
            pass

    def _get_route_maps(self):
        """Get route-map names"""

        map_name = None

        # Deletes table data
        DbOps.delete_rows('routemaps_back_end', self.device)

        try:
            route_map = self.send_command('show route-map | i route-map').splitlines()
            if route_map:
                for line in route_map:
                    if len(line.split()) == 0:
                        continue
                    elif line.split()[1] != map_name:
                        DbOps.update_route_maps(self.device, line.split()[1])

                    map_name = line.split()[1]
        except AttributeError:
            pass

    def _get_span_root(self):
        """Gets mac and arp tables. Concatinates into one"""

        # Delete table data
        DbOps.delete_rows('spanningtree_back_end', self.device)

        for vlan in self.send_command('show spanning-tree root | ex Vlan|-').splitlines():

            if len(vlan.split()) == 0:
                continue
            elif len(vlan.split()) == 7:
                DbOps.update_spann_tree_table(self.device, vlan.split()[0].strip('VLAN'), vlan.split()[1],
                                              vlan.split()[2], vlan.split()[3], '')
            elif len(vlan.split()) == 8:
                DbOps.update_spann_tree_table(self.device, vlan.split()[0].strip('VLAN'), vlan.split()[1],
                                              vlan.split()[2], vlan.split()[3], vlan.split()[7])

    def _get_mac_arp_table(self):
        """Gets mac and arp tables. Concatinates into one"""

        mac_table = []
        arp_table = []

        # Delete table data
        DbOps.delete_rows('arpmac_back_end', self.device)

        try:
            for mac in self.send_command('show mac address-table | ex Vlan|All|Total|%|-').splitlines():
                try:
                    mac_table.append({'vlan': mac.split()[0], 'address': mac.split()[1], 'type': mac.split()[2],
                                      'interface': mac.split()[3]})
                except IndexError:
                    continue

            # Gets and parse arp table response
            for arp in self.send_command('show ip arp | ex Protocol|Total|%').splitlines():
                try:
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
        except AttributeError:
            pass

    def _get_access_ports(self):
        """Get trunks"""

        # Deletes table data
        DbOps.delete_rows('accessinterfaces_back_end', self.device)

        try:
            for line in self.send_command('show interfaces status | ex Port').splitlines():
                if len(line.split()) == 0:
                    continue
                else:
                    if len(line.split()) == 7:
                        DbOps.update_access_interfaces_table(self.device, line.split()[0], line.split()[1],
                                                             line.split()[2],
                                                             line.split()[3],
                                                             line.split()[4], line.split()[5])
                    elif len(line.split()) == 6:
                        DbOps.update_access_interfaces_table(self.device, line.split()[0], 'N/A', line.split()[1],
                                                             line.split()[2],
                                                             line.split()[4], line.split()[5])
                    elif len(line.split()) == 5:
                        DbOps.update_access_interfaces_table(self.device, line.split()[0], 'N/A', line.split()[1],
                                                             line.split()[2],
                                                             line.split()[4], 'N/A')

        except AttributeError:
            pass

    def _get_vlans(self):
        """Get vlans"""

        # Deletes table data
        DbOps.delete_rows('vlans_back_end', self.device)

        try:
            for vlan in self.send_command('show vlan brief').splitlines():
                if len(vlan.split()) == 0:
                    continue
                elif vlan.split()[0] == '^':
                    break
                elif vlan.split()[0] == 'VLAN':
                    continue
                elif vlan.split()[0] == '----':
                    continue

                # Get vlan ports
                if vlan.split()[0].rfind("/") != -1:
                    vlan_ports = ' '.join(vlan.split())
                else:
                    vlan_ports = ' '.join(vlan.split()[3:])

                # Compare vlan id (show vlan) to vlan priority. Use indexing since vlan prio is VLAN + 4 ints, 0000
                for prio in self.send_command('show spanning-tree bridge priority').splitlines():
                    try:
                        if len(prio.split()) == 0:
                            continue
                        elif vlan.split()[0] == prio.split()[0][5:]:
                            DbOps.update_vlan_table(self.device, vlan.split()[0], prio.split()[1],
                                                    vlan.split()[1], vlan.split()[2], vlan_ports)
                            break
                        elif vlan.split()[0] == prio.split()[0][6:]:
                            DbOps.update_vlan_table(self.device, vlan.split()[0], prio.split()[1],
                                                    vlan.split()[1], vlan.split()[2], vlan_ports)
                            break
                        elif vlan.split()[0] == prio.split()[0][7]:
                            DbOps.update_vlan_table(self.device, vlan.split()[0], prio.split()[1],
                                                    vlan.split()[1], vlan.split()[2], vlan_ports)
                            break
                        else:
                            DbOps.update_vlan_table(self.device, vlan.split()[0], 'N/A',
                                                    vlan.split()[1], vlan.split()[2], vlan_ports)
                            break
                    except IndexError:
                        pass
        except AttributeError:
            pass

    def _get_hsrp_status(self):
        """Gets mac and arp tables. Concatinates into one"""

        # Delete table data
        DbOps.delete_rows('hsrp_back_end', self.device)

        try:
            for interface in self.send_command('show standby brief | ex Interface').splitlines():
                if len(interface.split()) == 0:
                    continue
                else:
                    try:
                        DbOps.update_hsrp_table(self.device, interface.split()[0], interface.split()[1],
                                                interface.split()[2], interface.split()[3], interface.split()[4],
                                                interface.split()[5], interface.split()[6], interface.split()[7])
                    except IndexError:
                        pass
        except AttributeError:
            pass

    def _get_ospf_routers(self):
        """Gets mac and arp tables. Concatinates into one"""

        process, router_id = None, None

        # Delete table data
        DbOps.delete_rows('ospfrouters_back_end', self.device)

        try:
            for line in self.send_command('show ip ospf border-routers | ex Codes|Internal|Base').splitlines():
                if len(line.split()) == 0:
                    continue
                elif line.split()[0] == 'OSPF':
                    router_id = line.split()[4].strip(')').strip('(')
                    process = line.split()[7].strip(')')
                elif len(line.split()) == 11:
                    DbOps.update_ospf_router_table(self.device, process, router_id, line.split()[1], line.split()[0],
                                                   line.split()[2].strip(']').strip('['), line.split()[4].strip(','),
                                                   line.split()[5].strip(','),
                                                   line.split()[6].strip(','),
                                                   f'{line.split()[7]} {line.split()[8].strip(",")}', line.split()[10])
        except AttributeError:
            pass

    def _get_dmvpn(self):
        """Gets dmvpn peers, attributes, status, writes to DB"""

        interface, router_type = None, None

        # Delete table data
        DbOps.delete_rows('dmvpn_back_end', self.device)

        try:
            for line in self.send_command('show dmvpn | b Interface').splitlines():
                if len(line.split()) == 0 or '-' in line or '#' in line:
                    continue
                elif len(line.split()) == 6:
                    DbOps.update_dmvpn_table(self.device, line.split()[1], line.split()[2],
                                             line.split()[3], line.split()[4], line.split()[5])
        except AttributeError:
            pass

    def _get_dmvpn_info(self):
        """Gets dmvpn peers, attributes, status, writes to DB"""

        interface = None
        # Delete table data
        DbOps.delete_rows('dmvpncount_back_end', self.device)
        try:
            for line in self.send_command('show dmvpn | i Interface|Type').splitlines():
                if len(line.split()) == 0:
                    continue
                elif len(line.split()) == 5:
                    interface = line.split()[1].strip(',')
                    get_dmvpn_interface(self.session, interface, self.device)
                elif len(line.split()) == 3:
                    router_type = line.split(':')[1].split(',')[0]
                    peer_count = line.split()[2].strip('Peers:').strip(',')
                    DbOps.update_dmvpn_count(self.device, interface, router_type, peer_count)
        except AttributeError:
            pass

    def _gather_facts(self):

        serial, model, uptime, software = None, None, None, None

        for i in self.send_command('show inventory').splitlines():

            if i.rfind('Chassis') != -1:
                model = i.split("\"")[3].split(' ')[1]
            elif i.rfind('NAME') != -1:
                model = i.split("\"")[1]

            if i.rfind('SN') != -1:
                serial = i.split('SN: ')[1]
                break

        for i in self.send_command('show version').splitlines():
            if i.rfind('Uptime') != -1:
                uptime = i.split("is")[2]
                break
            elif i.rfind('RELEASE SOFTWARE') != -1:
                software = i

        DbOps.update_device_facts(self.device, serial, model, uptime, software, self.username, self.password,
                                  self.ssh_port, self.netconf_port)
