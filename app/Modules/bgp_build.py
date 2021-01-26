"""Helper class to create configuration using ios-xe-native YANG model"""

import xml.etree.cElementTree as xml


class Templates:
    """Helper methods to build BGP policies"""

    def __init__(self, local_as):
        """Use init as a base for BGP config"""

        self.root = xml.Element("config")
        self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.native_element = xml.Element("native")
        self.native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
        self.root.append(self.native_element)
        self.router_elem = xml.SubElement(self.native_element, "router")
        self.bgp_elem = xml.SubElement(self.router_elem, "bgp")
        self.bgp_elem.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-bgp")
        self.bgp_as = xml.SubElement(self.bgp_elem, 'id')
        self.bgp_as.text = local_as

    def build_neighbor(self, addr_fam, remote_neighbor, neighbor_as, model, soft_reconf=None, next_hop=None, policy=None):
        """Build BGP neighbor policy"""

        print(addr_fam)
        neighbor = xml.SubElement(self.bgp_elem, "neighbor")
        neighbor_id = xml.SubElement(neighbor, "id")
        neighbor_id.text = remote_neighbor
        remote_as = xml.SubElement(neighbor, "remote-as")
        remote_as.text = neighbor_as

        if policy is not None:

            address_family_elem = xml.SubElement(self.bgp_elem, "address-family")
            vrf_elem = xml.SubElement(address_family_elem, "no-vrf")
            ipv4_elem = xml.SubElement(vrf_elem, "ipv4")
            v4_unicast = xml.SubElement(ipv4_elem, "af-name")
            v4_unicast.text = 'unicast'

            if model == 'ASR':
                v4_unicast_elem = xml.SubElement(v4_unicast, "ipv4-unicast")
                uni_neighbor = xml.SubElement(v4_unicast_elem, "neighbor")
            elif model == 'ISR' or model == 'CSR':
                uni_neighbor = xml.SubElement(ipv4_elem, "neighbor")
            else:
                uni_neighbor = xml.SubElement(ipv4_elem, "neighbor")

            neighbor_id = xml.SubElement(uni_neighbor, "id")
            neighbor_id.text = remote_neighbor

            if policy[1] != 'None':

                try:
                    if policy[2].split()[1] == 'route-map':
                        route_map_elem = xml.SubElement(uni_neighbor, "route-map")
                        in_out_elem = xml.SubElement(route_map_elem, "inout")
                        in_out_elem.text = policy[1]
                        route_map_name_elem = xml.SubElement(uni_neighbor, "route-map-name")
                        route_map_name_elem.text = policy[2].split()[0]
                except IndexError:
                    pass

                try:
                    if policy[2].split()[1] == 'prefix-list':
                        prefix_list_elem = xml.SubElement(uni_neighbor, "prefix-list")
                        in_out_elem = xml.SubElement(prefix_list_elem, "inout")
                        in_out_elem.text = policy[1]
                        prefix_name_elem = xml.SubElement(prefix_list_elem, "prefix-list-name")
                        prefix_name_elem.text = policy[2].split()[0]
                except IndexError:
                    pass

        if soft_reconf is not None:
            soft_recon_elem = xml.SubElement(uni_neighbor, "soft-reconfiguration")
            soft_recon_elem.text = 'inbound'
        if policy is not None:
            xml.SubElement(uni_neighbor, "next-hop-self")

        return self.root
