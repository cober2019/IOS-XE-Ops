
import app.Modules.connection as ConnectWith
import app.base.routes as Credentials
import app.Database.DbOperations as DbOps
from netmiko import ConnectHandler, ssh_exception
import csv

session = None

def send_command(command, expect_string=None):
    """Send Netmiko commands"""

    get_response = None

    retries = 0
    while retries != 3:
        try:
            get_response = session.send_command(command)
            break
        except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException):
            retries += 1

    return get_response


def get_serial_model(session_obj):
    """Get device serial number and model"""

    global session

    session = session_obj
    serial = None
    model = None

    show_inventory = send_command('show inventory')

    for i in show_inventory.splitlines():

        if i.rfind('Chassis') != -1:
            model = i.split("\"")[3].split(' ')[1]
        elif i.rfind('NAME') != -1:
            model = i.split("\"")[1]

        if i.rfind('SN') != -1:
            serial = i.split('SN: ')[1]
            break

    return serial, model


def get_uptime_software(session_obj):
    """Get device uptime and software"""

    global session

    session = session_obj
    uptime = None
    software = None
    show_version = send_command('show version')

    for i in show_version.splitlines():
        if i.rfind('Uptime') != -1:
            uptime = i.split("is")[2]
            break
        elif i.rfind('RELEASE SOFTWARE') != -1:
            software = i

    return uptime, software

def import_csv_bulk(path, filename):
    """Parse data from csv file upload, write to database devicefacts_front_end table"""

    with open(path) as file:
        for row_id, row in enumerate(csv.reader(file)):
            if row_id != 0:
                try:
                    netmiko_session = ConnectWith.creat_netmiko_connection(row[1], row[2], row[0], row[3])
                    serial_model = get_serial_model(netmiko_session)
                    uptime_software = get_uptime_software(netmiko_session)
                    update_facts = DbOps.update_device_facts(row[0], serial_model[0], serial_model[1], uptime_software[0],
                                                             uptime_software[1], row[1], row[2], row[3], row[4])
                except IndexError:
                    pass





