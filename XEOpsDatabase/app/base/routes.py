# -*- encoding: utf-8 -*-

from flask import jsonify, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm
import string
from app.base.models import User
from app.base.util import verify_pass
import app.Modules.connection as ConnectWith
import app.Modules.GetWithNetmiko as GetNetmiko
import app.Modules.GetWithNetconf as GetNeconf
import app.Modules.GetFacts as GetFacts
import app.Modules.ConfigValidation as ValidateConfig
import app.Modules.ConfigBuild as BuildConfig
import app.Database.DbOperations as DbOps
import app.Database.DatabaseQueries as QueryDbFor
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm.session import sessionmaker
import sqlite3
import logging
import os

app_config = None
device = None
username = None
password = None
netconf_port = None
ssh_port = None
netconf_session = None
netmiko_session = None
model = None

log_dir = os.path.dirname(os.path.realpath(__file__)).replace('base', 'logs\\')
logging.basicConfig(filename=f'{log_dir}sessionlog.log', level=logging.INFO)
allowed_extension = {'xlsx', 'csv'}


@blueprint.route('/')
def route_default():
    return render_template('inventory.html', inventory=QueryDbFor.query_device_inventory())


@blueprint.route('/add_inventory', methods=['POST', 'GET'])
def add_devices():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        netconf_port = request.form['netconf']
        ssh_port = request.form['ssh']

        if not netconf_port:
            netconf_port = 830
        if not ssh_port:
            ssh_port = 22

        # Attempt to create connection objects. Must have both to get to homepage
        netconf_session = ConnectWith.create_netconf_connection(request.form['username'], request.form['password'],
                                                                request.form['device'], netconf_port)
        netmiko_session = ConnectWith.creat_netmiko_connection(request.form['username'], request.form['password'],
                                                               request.form['device'], ssh_port)

        # Using netmiko and ncclient for connections, verify that both pass. If one fails, return to login
        if netmiko_session == 'Authenitcation Error':
            flash("Authentication Failure")
            return redirect(url_for('base_blueprint.add_devices'))
        elif netmiko_session == 'ssh_exception' or netmiko_session == 'Connection Timeout':
            flash("Check Device Connectivity")
            return redirect(url_for('base_blueprint.add_devices'))

        if netconf_session == 'Authentication Error':
            flash("Authentication Failure")
            return redirect(url_for('base_blueprint.add_devices'))
        elif netconf_session == 'Connection Timeout' or netconf_session == 'Connectivity Issue':
            flash("Check Device Connectivity")
            return redirect(url_for('base_blueprint.add_devices'))
        else:
            serial_model = GetFacts.get_serial_model(netmiko_session)
            uptime_software = GetFacts.get_serial_model(netmiko_session)
            DbOps.update_device_facts(request.form['device'], serial_model[0], serial_model[1], uptime_software[0],
                                      uptime_software[1], request.form['username'], request.form['password'],
                                      ssh_port, netconf_port)

            return redirect(url_for('base_blueprint.route_default'))

    else:
        return render_template('accounts/new_inventory_login.html', form=login_form)


@blueprint.route('/add_bulk_devices', methods=['GET', 'POST'])
def add_bulk_devices():
    return render_template('add_bulk_devices.html')


@blueprint.route('/upload_csv', methods=['GET', 'POST'])
def upload_file():
    """Upload new device from csv file"""

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return render_template('add_bulk_devices.html', invalid='Invalid Extension | .CSV Only!')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template('add_bulk_devices.html', invalid='Filename Can\'t Be Empty')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(f'{os.getcwd()}\\app\\uploads', filename))
            GetFacts.import_csv_bulk(os.path.join(f'{os.getcwd()}\\app\\uploads', filename), filename)

            return redirect(url_for('base_blueprint.route_default'))

    return render_template('add_bulk_devices.html', invalid='Invalid File | .CSV Only!')


@blueprint.route('/login/<host>', methods=['POST', 'GET'])
def login(host):
    global device, username, password, netconf_session, netmiko_session, model, netconf_port, ssh_port

    login_form = LoginForm(request.form)
    if 'login' in request.form:

        device = host
        username = request.form['username']
        password = request.form['password']
        netconf_port = request.form['netconf']
        ssh_port = request.form['ssh']

        if not netconf_port:
            netconf_port = 830
        if not ssh_port:
            ssh_port = 22

        if device and username and password:

            # Attempt to create connection objects. Must have both to get to homepage
            netconf_session = ConnectWith.create_netconf_connection(request.form['username'], request.form['password'],
                                                                    host, netconf_port)
            netmiko_session = ConnectWith.creat_netmiko_connection(request.form['username'], request.form['password'],
                                                                   host, ssh_port)

            # Using netmiko and ncclient for connections, verify that both pass. If one fails, return to login
            if netmiko_session == 'Authenitcation Error':
                flash("Authentication Failure")
                return redirect(url_for('base_blueprint.login'))
            elif netmiko_session == 'ssh_exception' or netmiko_session == 'Connection Timeout':
                flash("Check Device Connectivity")
                return redirect(url_for('base_blueprint.login'))

            if netconf_session == 'Authentication Error':
                flash("Authentication Failure")
                return redirect(url_for('base_blueprint.login'))
            elif netconf_session == 'Connection Timeout' or netconf_session == 'Connectivity Issue':
                flash("Check Device Connectivity")
                return redirect(url_for('base_blueprint.login', host=host))
            else:
                return redirect(url_for('base_blueprint.gather_facts'))

    else:
        return render_template('accounts/login.html', form=login_form, host=host)


@blueprint.route('/logout')
def logout():
    """User logout and re-login"""

    logout_user()
    return redirect(url_for('base_blueprint.route_default'))


@blueprint.route('/gather_facts')
def gather_facts():
    """Gets all things routing, arp, interfaces, routing protocols"""

    global model

    serial_model = GetFacts.get_serial_model(netmiko_session)
    model = serial_model[1]
    uptime_software = GetFacts.get_uptime_software(netmiko_session)
    update_facts = DbOps.update_device_facts(device, serial_model[0], serial_model[1], uptime_software[0],
                                             uptime_software[1], username, password, ssh_port, netconf_port)

    if update_facts is not None:
        GetNeconf.start_polling(username, password, device, serial_model[1][:3], netconf_port, ssh_port)
        GetNetmiko.start_polling(username, password, device, serial_model[1][:3], ssh_port)

    return redirect(url_for('base_blueprint.index'))


@blueprint.route('/index')
def index():
    """Gets all things routing, arp, interfaces, routing protocols"""
    return render_template('index.html', interfaces=QueryDbFor.query_interfaces(device),
                           bgp=QueryDbFor.query_bgp_status(device), ospf=QueryDbFor.query_ospf_status(device),
                           arp=QueryDbFor.query_arp_table(device), hsrp=QueryDbFor.query_hsrp(device),
                           border_routers=QueryDbFor.query_ospf_routers(device), device=device)


@blueprint.route('/index', methods=['POST'])
def table_refresh():
    """Used for table refreshes"""

    # Get for attribute 'name', match condition, refresh data table

    if request.form.get('action') == 'arp':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'arp')
        return jsonify({'data': render_template('refresh_arp.html', arps=QueryDbFor.query_arp_table(device))})
    elif request.form.get('action') == 'bgp':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'bgp')
        return jsonify({'data': render_template('refresh_bgp.html', bgp=QueryDbFor.query_bgp_status(device))})
    elif request.form.get('action') == 'ospf':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'ospf')
        return jsonify({'data': render_template('refresh_ospf.html', ospf=QueryDbFor.query_ospf_status(device))})
    elif request.form.get('action') == 'mac':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'mac')
        return jsonify({'data': render_template('refresh_mac.html', mac_arp=QueryDbFor.query_mac_to_arp(device))})
    elif request.form.get('action') == 'cdp':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'cdp')
        return jsonify({'data': render_template('refresh_cdp.html', neighbors=QueryDbFor.query_cdp(device))})
    elif request.form.get('action') == 'access':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'access')
        return jsonify({'data': render_template('refresh_access.html', access_ports=QueryDbFor.query_access_ports(device))})
    elif request.form.get('action') == 'span':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'span')
        return jsonify({'data': render_template('refresh_span.html', roots=QueryDbFor.query_spanning_tree(device))})
    elif request.form.get('action') == 'clearArp':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'clearArp')
        return jsonify({'data': render_template('refresh_arp.html', arp=QueryDbFor.query_arp_table(device))})
    elif request.form.get('action') == 'refreshArp':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'refreshArp')
        return jsonify({'data': render_template('refresh_arp.html', arp=QueryDbFor.query_arp_table(device))})
    elif request.form.get('action') == 'vlans':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'vlans')
        return jsonify({'data': render_template('refresh_vlans.html', vlans=QueryDbFor.query_vlans(device))})
    elif request.form.get('action') == 'portChannel':
        GetNeconf.indivisual_poll(username, password, device, netconf_port, 'portchannel')
        return jsonify({'data': render_template('refresh_port_channels.html', port_chan=QueryDbFor.query_port_channels(device))})
    elif request.form.get('action') == 'trunks':
        GetNeconf.indivisual_poll(username, password, device, netconf_port, 'trunks', ssh_port=ssh_port)
        return jsonify({'data': render_template('refresh_trunks.html', trunks=QueryDbFor.query_trunks(device))})
    elif request.form.get('action') == 'interfaces':
        GetNeconf.indivisual_poll(username, password, device, netconf_port, 'interfaces')
        return jsonify({'data': render_template('refresh_table.html', interfaces=QueryDbFor.query_interfaces(device))})
    elif request.form.get('action') == 'hsrp':
        GetNeconf.indivisual_poll(username, password, device, netconf_port, 'hsrp')
        return jsonify({'data': render_template('refresh_hsrp.html', hsrp=QueryDbFor.query_hsrp(device))})
    elif request.form.get('action') == 'peer_count':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'peer_count')
        return jsonify({'data': render_template('dmvpn_peer_refresh.html', dmvpn_status=QueryDbFor.query_dmvpn_status(device))})
    elif request.form.get('action') == 'borderRouters':
        GetNetmiko.indivisual_poll(username, password, device, ssh_port, 'borderRouters')
        return jsonify({'data': render_template('refresh_border_routers.html', border_routers=QueryDbFor.query_ospf_routers(device))})


@blueprint.route('/routing_table')
def routing_table():
    """Gets IOS-XE routing table"""

    return render_template('get_routing.html', route_table=QueryDbFor.query_routes(device))


@blueprint.route('/int_details', methods=['POST'])
def interface_details():
    """Get interface details, CLI view"""

    return render_template('more_int_detials.html',
                           details=GetNetmiko.more_int_details(netmiko_session, request.form.get('details')))


@blueprint.route('/cdp_details', methods=['POST'])
def cdp_interface_details():
    """Get cdp neighbor detail, CLI view"""

    return render_template('more_int_detials.html',
                           details=GetNetmiko.get_cdp_neighbors_detail(netmiko_session, request.form.get('details')))


@blueprint.route('/span_details', methods=['POST'])
def span_details():
    """Get spanning tree vlan details, CLI view"""

    return render_template('more_int_detials.html',
                           details=GetNetmiko.get_span_detail(netmiko_session, request.form.get('details')))

@blueprint.route('/hsrp_details', methods=['POST'])
def hsrp_details():
    """Get HSRP details, CLI view"""

    # Get HSRP details. Strip 'HSRP' off the JS Value.
    details = GetNetmiko.get_hsrp_detail(netmiko_session, request.form.get('details').strip('HSRP'))

    return render_template('more_int_detials.html', hsrp_int=details[0], hsrp_neighbor=details[1])


@blueprint.route('/qos_details', methods=['POST'])
def qos_interface_details():
    """Gets Qos details, CLI view"""

    return render_template('more_qos_detials.html',
                           details=GetNetmiko.get_router_lsas(netmiko_session, request.form.get('details')))

@blueprint.route('/adv_lsas_details', methods=['POST'])
def adv_lsas_details():
    """Gets Qos details, CLI view"""

    return render_template('adv_lsas_details.html',
                           details=GetNetmiko.get(netmiko_session, request.form.get('details')))

@blueprint.route('/route_details', methods=['POST'])
def route_details():
    """Gets ip route details, CLI view"""

    details = request.form.get('details').split('-')
    route_details = GetNetmiko.get_route_detials(netmiko_session, details[0].split('/')[0], details[1])

    return render_template('route_detials.html', route=route_details[0], route_detials=route_details[1])


@blueprint.route('/qos')
def get_qos():
    """Gets Qos policy stats, CLI view"""

    return render_template('qos.html', interfaces=QueryDbFor.query_interfaces(device),
                           interface_qos=QueryDbFor.query_qos(device))


@blueprint.route('/modify_qos/<interface>')
def configure_qos(interface):
    """Render QOS configuration/Form"""

    return render_template('modify_qos.html', interface=interface.replace('%2f', '/'), policies=service_policies)


@blueprint.route('/modify_qos', methods=['POST'])
def apply_qos():
    """POST QOS configuration from form data"""

    find_int_num = [i for i in request.form.get("interface") if i not in string.ascii_letters]
    find_int_type = [i for i in request.form.get("interface") if i in string.ascii_letters]
    build_config = BuildConfig.build_interface_qos(''.join(find_int_type) + ''.join(find_int_num),
                                                   request.form.get("servicePolicy"),
                                                   request.form.get("direction"))

    return redirect(url_for('base_blueprint.index'))


@blueprint.route('/modify_inteface/<interface>', methods=['POST', 'GET'])
def modify_inteface(interface):
    """Renders and build configurations for interface modification"""

    if not request.form:
        current_config = GetNetmiko.current_int_config(netmiko_session, interface.replace('%2f', '/'))

        return render_template('modify_interface.html', interface=interface.replace('%2f', '/'),
                               vrfs=QueryDbFor.query_vrfs(device), current_config=current_config,
                               mgmt_int=[i for i in QueryDbFor.query_interfaces(device) if i.id == device],
                               model=model[:3][-2:])
    else:
        status = BuildConfig.parse_int_form(request.form, device, password, username)
        current_config = GetNetmiko.current_int_config(netmiko_session, interface.replace('%2f', '/'))

        return render_template('modify_interface.html', interface=interface.replace('%2f', '/'),
                               vrfs=QueryDbFor.query_vrfs(device),
                               mgmt_int=[i for i in QueryDbFor.query_interfaces(device) if i.id == device],
                               current_config=current_config, model=model[:3][-2:], status=status)


@blueprint.route('/new_int_form', methods=['POST', 'GET'])
def new_interface():
    """POST new interface"""

    if not request.form:
        return render_template('new_int_form.html', vrfs=QueryDbFor.query_vrfs(device))
    else:
        status = BuildConfig.parse_int_form(request.form, device, password, username)
        interface = request.form.get('newIntCustomForm').splitlines()
        current_config = GetNetmiko.current_int_config(netmiko_session, interface[0].split()[1])

        return render_template('new_int_form.html', vrfs=QueryDbFor.query_vrfs(device), current_config=current_config,
                               status=status)


@blueprint.route('/ping/<source>', methods=['POST', 'GET'])
def ping(source):
    """Renders ping form and sends ping"""

    if not request.form:
        return render_template('ping.html', source=source.replace('%2f', '/'), vrfs=QueryDbFor.query_vrfs(device))
    else:
        if request.form.get('vrf') == 'none':
            ping = GetNetmiko.send_ping(netmiko_session, netmiko_session, username, password, device,
                                        request.form.get('dest'), request.form.get('source'), request.form.get('count'))
        else:
            ping = GetNetmiko.send_ping(netmiko_session, username, password, device, request.form.get('dest'),
                                        request.form.get('source'), request.form.get('count'), vrf=request.form.get('vrf'))

        return render_template('ping.html', source=source.replace('%2f', '/'), vrfs=QueryDbFor.query_vrfs(device), results=ping)


@blueprint.route('/layer2')
def layer_2():
    """Gets layer two information from the device"""

    return render_template('get_layer_two.html', neighbors=QueryDbFor.query_cdp(device),
                           vlans=QueryDbFor.query_vlans(device),
                           trunks=QueryDbFor.query_trunks(device), access_ports=QueryDbFor.query_access_ports(device),
                           port_chan=QueryDbFor.query_port_channels(device),
                           roots=QueryDbFor.query_spanning_tree(device),
                           mac_arp=QueryDbFor.query_mac_to_arp(device), model=model)


@blueprint.route('/add_vlan', methods=['POST', 'GET'])
def add_vlan():
    """Renders vlan configuration form"""

    if not request.form:
        return render_template('add_vlan.html', access_ports=QueryDbFor.query_access_ports(device),
                               port_channels=QueryDbFor.query_port_channels(device), vlans=QueryDbFor.query_vlans(device))
    else:
        status = BuildConfig.parse_add_vlan_form(request.form, device, password, username)

        return render_template('add_vlan.html', access_ports=QueryDbFor.query_access_ports(device),
                               port_channels=QueryDbFor.query_port_channels(device), vlans=QueryDbFor.query_vlans(device),
                               status=status)

@blueprint.route('/add_poch', methods=['POST', 'GET'])
def add_poch():
    """Renders vlan configuration form"""

    # Remove duplicate channel-group numbers for html dropdown
    groups = [i.group for i in QueryDbFor.query_port_channels(device)]

    if not request.form:
        return render_template('add_poch.html', interfaces=QueryDbFor.query_interfaces(device),
                               port_channels=list(dict.fromkeys(groups)), int_status=QueryDbFor.query_access_ports(device))
    else:
        channel_mode = [i.mode for i in QueryDbFor.query_port_channels(device) if request.form.get('pochannel') == i.group]
        status = BuildConfig.parse_poch_interface(request.form, list(dict.fromkeys(channel_mode)), device, password, username)
        current_config = GetNetmiko.current_int_config(netmiko_session, request.form.get('interface'))

        return render_template('add_poch.html', interfaces=QueryDbFor.query_interfaces(device),
                               port_channels=groups, int_status=QueryDbFor.query_access_ports(device),
                               current_config=current_config, status=status)

@blueprint.route('/add_ospf_neighbor')
def add_ospf_neighbor():
    """Render OSPF configuration/Form"""

    return render_template('add_ospf_neighbor.html', ospf_proc=QueryDbFor.query_ospf_processes(device))


@blueprint.route('/add_bgp_neighbor')
def add_bgp_neighbor():
    """POST BGP configuration from form data"""

    # Remove duplicate prefix-list names for html dropdown
    lists = [i.name for i in QueryDbFor.query_prefix_list(device)]

    return render_template('add_bgp_neighbor.html', prefixes=list(dict.fromkeys(lists)),
                           route_map=QueryDbFor.query_route_maps(device))


@blueprint.route('/add_routing_neighbor', methods=['POST'])
def post_routing_neighbor():
    """POST OSPF configuration from form data"""

    BuildConfig.parse_routing_config(form, device, password, username)

    return redirect(url_for('base_blueprint.index'))


@blueprint.route('/modify_access_int/<interface>', methods=['POST', 'GET'])
def modify_access_interface(interface):
    """POST BGP configuration from form data"""

    if not request.form:
        current_config = GetNetmiko.current_int_config(netmiko_session, interface.replace('%2f', '/'))

        return render_template('modify_access_int.html', interface=interface.replace('%2f', '/'),
                               current_config=current_config, vlans=QueryDbFor.query_vlans(device))
    else:
        status = BuildConfig.parse_access_int_form(request.form, device, password, username)
        current_config = GetNetmiko.current_int_config(netmiko_session, interface.replace('%2f', '/'))

        return render_template('modify_access_int.html', interface=interface.replace('%2f', '/'),
                               current_config=current_config, vlans=QueryDbFor.query_vlans(device), status=status)


@blueprint.route('/modify_trunk_int/<interface>', methods=['POST', 'GET'])
def modify_trunk_interface(interface):
    """Render trunk modification page"""

    if not request.form:
        current_config = GetNetmiko.current_int_config(netmiko_session, interface.replace('%2f', '/'))

        return render_template('modify_trunk_int.html', interface=interface.replace('%2f', '/'),
                               current_config=current_config, vlans=QueryDbFor.query_vlans(device))
    else:
        status = BuildConfig.parse_trunk_interface(request.form, device, password, username)
        current_config = GetNetmiko.current_int_config(netmiko_session, interface.replace('%2f', '/'))

        return render_template('modify_trunk_int.html', interface=interface.replace('%2f', '/'),
                               current_config=current_config, vlans=QueryDbFor.query_vlans(device), status=status)

@blueprint.route('/dmvpn')
def dmvpn():
    """Gets layer two information from the device"""

    return render_template('get_dmvpn.html', dmvpn_status=QueryDbFor.query_dmvpn_status(device),
                           dmvpn_peer_count=QueryDbFor.query_dmvpn_type(device), dmvpn_ints=QueryDbFor.query_dmvpn_interfaces(device),
                           ospf=QueryDbFor.query_ospf_status(device), border_routers=QueryDbFor.query_ospf_routers(device),
                           ints=QueryDbFor.query_interfaces(device))


@blueprint.route('/new_dmvpn_int', methods=['POST', 'GET'])
def new_dmvpn_interface():
    """POST new interface"""

    if not request.form:
        return render_template('new_dmvpn_int.html', vrfs=QueryDbFor.query_vrfs(device))
    else:
        status = BuildConfig.parse_int_form(request.form, device, password, username)
        interface = request.form.get('newIntCustomForm').splitlines()
        current_config = GetNetmiko.current_int_config(netmiko_session, interface[0].split()[1])

        return render_template('new_dmvpn_int.html')

@blueprint.route('/about')
def about():
    """Program info"""

    return render_template('about.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extension
