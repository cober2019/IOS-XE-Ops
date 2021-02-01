import os
import sys
import re
import csv
import time
import ipaddress
import netmiko
from netmiko import ConnectHandler


def appy_mac(interface, mac):

    config_portsec_commands = ["interface gigabitEthernet0/2", "switchport mode access",
                               "switchport access vlan 11", "switchport port-security",
                               "switchport port-security mac-address sticky"]
    add_static_mac = ["switchport port-security mac-address sticky "]

def findMACAddress(str):
    cisco_mac_regex = "([a-fA-F0-9]{4}[\.]?)"
    p = re.compile(cisco_mac_regex)
    result = re.findall(p, str)
    result_joined = ''.join(result)
    # print (result_joined)
    add_static_mac.append(result_joined)
    return result_joined


def checkMACAddress(str):
    result = re.match(r"([a-fA-F0-9]{4}[\.]?)", str)
    if result == True:
        return (bool(result))
    else:
        return (bool(result))


def convert_list_to_string(list_object, seperator=''):
    return seperator.join(list_object)


# testmac = "0000.4332.5544"

try:
    with open('rec_list.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print ("Skip first Line")
                line_count += 1
            else:
                host = convert_list_to_string(row[0])
                rec_ip = convert_list_to_string(row[1])
                svi = convert_list_to_string(row[2])
                #
                device = ConnectHandler(device_type='cisco_ios', ip=host, username='cisco', password='cisco',
                                        secret='cisco')
                device.enable()
                output1 = device.send_command("show mac address-table interface gigabitEthernet0/2")
                #
                # print (host)
                # print ("##########\n")
                # print (output1)
                check_mac_value = findMACAddress(output1)
                MACCHECK = checkMACAddress(check_mac_value)
                line_count += 1
                # print ("Count added")
                if MACCHECK == True:
                    static_conf = ''.join(add_static_mac)
                    config_portsec_commands.append(static_conf)
                    outF = open("SwitchLog-" + host + ".txt", "a")
                    output2 = device.send_command("show run interface gigabitEthernet0/2")
                    outF.write("Switch " + host + " Pre Port Config Change # \n")
                    outF.write("\n")
                    outF.write(output2)
                    outF.write("\n")
                    outF.write("################\n")
                    outF.write("################\n")
                    configdev = device.send_config_set(config_portsec_commands)
                    output3 = device.send_command("show run interface gigabitEthernet0/2")
                    outF.write("Switch " + host + " After Port Config Change # \n")
                    outF.write("\n")
                    outF.write(output3)
                    outF.write("\n")
                    outF.write("################\n")
                    outF.write("################\n")
                    print(host + " Completed")
                    device.send_command("write memory\n")
                    device.disconnect()
                    operationLOG = open("OperationLog.txt", "a")
                    operationLOG.write("Switch " + host + " Completed \n")
                elif MACCHECK == False:
                    print("NULL MAC ADDRESS")
                    remove_vlan_interface_commands = ["no interface vlan 11"]
                    config_vlan_interface_commands = ["interface vlan 11", "no shutdown"]
                    add_svi = ["ip address ", " 255.255.255.0"]
                    add_svi.insert(1, svi)
                    oneliner = ''.join(add_svi)
                    config_vlan_interface_commands.append(oneliner)
                    print(add_svi)
                    print(oneliner)
                    print(config_vlan_interface_commands)
                    configdev = device.send_config_set(config_portsec_commands)
                    configdev2 = device.send_config_set(config_vlan_interface_commands)
                    time.sleep(2)
                    output4 = device.send_command("ping " + rec_ip + " repeat 10")
                    configdev3 = device.send_config_set(remove_vlan_interface_commands)
                    device.send_command("write memory\n")
                    device.disconnect()
                    print(host + " Completed")
                else:
                    print("NOTHING WAS DONE to host" + host)
        print(f'Processed {line_count} lines.')
except:
    print("\nBroken")