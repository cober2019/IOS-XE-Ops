""" Collection of funtions used to send, save, and validate XML responses"""

import os
import time
import lxml.etree as ET
import xml.etree.cElementTree as xml
from ncclient import manager


def save_config_to_file(configuration):
    """Save config to file"""

    # Convert configu to string
    format_str = prepare_config(configuration)
    # Get current path and replace directory to configs folder
    configs_dir = os.path.dirname(os.path.realpath(__file__)).replace('Modules', 'configs\\')
    # Open or create file if not in directory, write and close
    config = open(f'{configs_dir}{str(time.asctime()).replace(":", "-").replace(" ", "-")}.xml', 'w')
    config.write(format_str)
    config.close()


def prepare_config(config):
    """Prepare config for sending directly from string"""

    xmlstr = xml.tostring(config, method='xml')
    converted_config = xmlstr.decode('utf-8')

    return converted_config


def check_rpc_reply(response, configuration=None):
    """Checks RPC Reply for string. Notifies user config was saved"""

    if response.rfind("Save running-config successful") != -1:
        return 'Configuration Saved'
    elif response.rfind("<ok/>") != -1:
        save_config_to_file(configuration)
        return 'Success'
    elif response.rfind("<data></data>") != -1:
        # Recieve sucessful but empty RPC reply
        return 'Empty Config'


def save_running_config(session):
    """Save new configuration to running config"""

    save_payload = """
                       <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
                       """
    try:
        response = session.dispatch(ET.fromstring(save_payload)).xml
        validate_response = check_rpc_reply(response)
    except manager.operations.errors.TimeoutExpiredError as error:
        validate_response = [error, 'Connection Timeout']
    except AttributeError as error:
        validate_response = [error, 'Session Expired']
    except manager.transport.TransportError as error:
        validate_response = [error, 'Transport Error']
    except manager.operations.rpc.RPCError as error:
        validate_response = [error, 'Configuration Failed']

    response = prepare_response(validate_response)

    return response


def prepare_response(send_config):
    """Prepares response for /routes use"""

    if send_config[1] == 'Connection Timeout':
        response = send_config[0]
    elif send_config[1] == 'Session Expired':
        response = send_config[0]
    elif send_config[1] == 'Transport Error':
        response = send_config[0]
    elif send_config[1] == 'Configuration Failed':
        response = send_config[0]
    elif send_config == 'Success':
        response = 'Success'
    else:
        response = 'Configuration Failed'

    return response


def send_configuration(netconf_session, config):
    """Send configuration via NETCONF"""

    formatted_config = prepare_config(config)

    try:
        response = netconf_session.edit_config(formatted_config, target="running")
        validate_response = check_rpc_reply(str(response), config)
    except manager.operations.errors.TimeoutExpiredError as error:
        save_config_to_file(config)
        validate_response = [error, 'Connection Timeout']
    except AttributeError as error:
        save_config_to_file(config)
        validate_response = [error, 'Session Expired']
    except manager.transport.TransportError as error:
        save_config_to_file(config)
        validate_response = [error, 'Transport Error']
    except manager.operations.rpc.RPCError as error:
        save_config_to_file(config)
        validate_response = [error, 'Configuration Failed']

    response = prepare_response(validate_response)

    return response
