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

    return device_connect


def netmiko_w_enable(host: str = None, username: str = None, password: str = None, **enable) -> object:
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
    except manager.operations.errors.TimeoutExpiredError as error:
        netconf_session = [error, 'Connection Timeout', 'error']
    except AttributeError as error:
        netconf_session = [error, 'Session Expired', 'error']
    except manager.transport.TransportError as error:
        netconf_session = [error, 'Transport Error', 'error']
    except manager.operations.rpc.RPCError as error:
        netconf_session = [error, 'Configuration Failed', 'error']

    return netconf_session
