"""NCClient connection funtion"""

from netmiko import ConnectHandler, ssh_exception
from ncclient import manager


def creat_netmiko_connection(username, password, host, port) -> object:
    """Logs into device and returns a connection object to the caller. """

    credentials = {
        'device_type': 'cisco_ios',
        'host': host,
        'username': username,
        'password': password,
        'port': port,
        'session_log': 'my_file.out'}

    try:
        device_connect = ConnectHandler(**credentials)
    except ssh_exception.AuthenticationException:
        device_connect = "ssh_exception"
    except EOFError:
        device_connect = "Authenitcation Error"
    except ssh_exception.NetmikoTimeoutException:
        device_connect = 'Connection Timeout'
    except ValueError:
        device_connect = 'Connection iSSUE'

    return device_connect


def netmiko_w_enable(host, username, password, **enable) -> object:
    """Logs into device and returns a connection object to the caller. """

    try:
        credentials = {
            'device_type': 'cisco_asa',
            'host': host,
            'username': username,
            'password': password,
            'secret': enable["enable_pass"],
            'session_log': 'my_file.out'}

        try:
            device_connect = ConnectHandler(**credentials)
        except ssh_exception.AuthenticationException:
            raise ConnectionError("Could not connect to device {}".format(host))

        return device_connect

    except KeyError:
        pass


def create_netconf_connection(username, password, host, port) -> manager:
    """Creates NETCONF Session"""

    try:

        netconf_session = manager.connect(host=host, port=port, username=username,
                                          password=password,
                                          device_params={'name': 'csr'})
        
    except manager.operations.errors.TimeoutExpiredError:
        netconf_session = 'error'
    except AttributeError as error:
        netconf_session = 'error'
    except manager.transport.TransportError:
        netconf_session = 'error'
    except manager.operations.rpc.RPCError:
        netconf_session = 'error'

    return netconf_session


def re_auth_netconf(username, password, host, port):
    
    netconf_session = create_netconf_connection(username, password, host, port)
    
    return netconf_session


def re_auth_netmiko(username, password, host, port):
    
    netmiko_session = creat_netmiko_connection(username, password, host, port)

    return netmiko_session