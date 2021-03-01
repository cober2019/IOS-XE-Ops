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
        device_connect = 'Connection Issue'
    except:
        device_connect = 'An Error Occured'

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

    retries = 0
    netconf_session = 'error'

    # Attempt connection 3 times
    while retries != 3:
        try:

            netconf_session = manager.connect(host=host, port=port, username=username,
                                              password=password,
                                              device_params={'name': 'csr'})
            break
        except manager.operations.errors.TimeoutExpiredError:
            retries += 1
        except AttributeError:
            retries += 1
        except manager.transport.TransportError:
            retries += 1
        except manager.operations.rpc.RPCError:
            retries += 1
        except OSError:
            retries += 1

    return netconf_session


def re_auth_netconf(username, password, host, port):
    
    netconf_session = create_netconf_connection(username, password, host, port)
    
    return netconf_session


def re_auth_netmiko(username, password, host, port):
    
    netmiko_session = creat_netmiko_connection(username, password, host, port)

    return netmiko_session