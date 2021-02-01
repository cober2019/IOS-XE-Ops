"""Helper class to that builds interface configs"""

import xml.etree.cElementTree as xml


class Templates:
    """Helper method that build OSPF configs"""

    def __init__(self, int_type, name):

        self.root = xml.Element("config")
        self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.native_element = xml.Element("native")
        self.native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
        self.root.append(self.native_element)
        self.interface = xml.SubElement(self.native_element, "interface")
        self.interface_type = xml.SubElement(self.interface, int_type)
        self.interface_name = xml.SubElement(self.interface_type, 'name')
        self.interface_name.text = name

    def build_interface(self, host, subnet, admin, descr, vrf, negotiation, mac):
        print(admin)

        if host is not None:
            ip_elem = xml.SubElement(self.interface_type, "ip")
            address_ele = xml.SubElement(ip_elem, "address")
            primary_ele = xml.SubElement(address_ele, "primary")
            address = xml.SubElement(primary_ele, "address")
            address.text = host
            mask = xml.SubElement(primary_ele, "mask")
            mask.text = subnet

        if admin == 'down':
            xml.SubElement(self.interface_type, "shutdown")
        elif admin == 'no shutdown':
            xml.SubElement(self.interface_type, "shutdown operation=\"delete\"")
        elif admin == 'up':
            pass

        if descr is not None:
            description = xml.SubElement(self.interface_type, "description")
            description.text = descr

        if vrf != 'No-vrf':
            vrf_ele = xml.SubElement(self.interface_type, "vrf")
            forward = xml.SubElement(vrf_ele, "forwarding")
            forward.text = vrf

        if negotiation is not None:
            negotiation_elem = xml.SubElement(self.interface_type, "negotiation")
            negotiation_elem.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet")
            auto = xml.SubElement(negotiation_elem, "auto")
            auto.text = negotiation


        return self.root
