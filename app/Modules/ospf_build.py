"""Helper class to create configuration using ios-xe-native YANG model"""

import xml.etree.cElementTree as xml


class Templates:
    """Helper methods to create class-maps using YANG models"""

    def __init__(self, process):
        self.root = xml.Element("config")
        self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.native_element = xml.Element("native")
        self.native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
        self.root.append(self.native_element)
        self.router_elem = xml.SubElement(self.native_element, "router")
        self.ospf_elem = xml.SubElement(self.router_elem, "ospf")
        self.ospf_elem.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-ospf")
        self.ospf_as = xml.SubElement(self.ospf_elem, 'id')
        self.ospf_as.text = process

    def build_neighbor(self, network, wildcard, area):
        network_elem = xml.SubElement(self.ospf_elem, "network")
        ip_network = xml.SubElement(network_elem, "ip")
        ip_network.text = network
        wildcard_mask = xml.SubElement(network_elem, "mask")
        wildcard_mask.text = wildcard
        network_area = xml.SubElement(network_elem, "area")
        network_area.text = area

        return self.root
