"""Configuration validation"""

def validate_vlan(id, name, vlans):

    id_exist = 0
    for i in vlans:
        if i.vlan_id == id:
            id_exist = 1

    name_exist = 0
    for i in vlans:
        if i.name == name:
            name_exist = 1

    return id_exist, name_exist

def validate_interface(interface, ip, mask, status, vrf, descr, interfaces):
    
    ip_exist = 0
    for i in interfaces:
        if i.ip_mac.split('/')[0] == ip:
            ip_exist = 1
        
    return ip_exist


def validate_text_bgp(config):

    valid = 0
    if 'router bgp' in config:
        valid = 1

    return valid


def validate_text_ospf(config):

    valid = 0
    if 'router ospf' in config:
        valid = 1

    return valid