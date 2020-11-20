"""Helper class to create configuration using ios-xe-native YANG model"""

import xml.etree.cElementTree as xml


def build_policy(interface_type, interface_name, direction, policy):

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    interface = xml.SubElement(native_element, "interface")
    int_type = xml.SubElement(interface, interface_type)
    int_num = xml.SubElement(int_type, 'name')
    int_num.text = interface_name
    service_policy = xml.SubElement(int_type, "service-policy")
    service_policy.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")
    direction = xml.SubElement(service_policy, direction)
    direction.text = policy

    return root
