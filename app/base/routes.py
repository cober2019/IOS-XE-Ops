# -*- encoding: utf-8 -*-

from flask import jsonify, render_template, redirect, request, url_for, flash
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
from app.Modules.ProjectRouting.Software import IOSXE
import app.Modules.ProjectRouting.Database.DB_queries as Db_queries
import app.Modules.ProjectRouting.Database.DatabaseOps as DB
import app.Modules.connection as ConnectWith
import app.Modules.GetInterfaces as GetInterfacesInfo
import app.Modules.GetWithNetmiko as GetInfo
import app.Modules.InterfacesQoS as GetQos
import app.Modules.bgp_build as Build_bgp_config
import app.Modules.ospf_build as Build_ospf_config
import app.Modules.netconfsend as SendConfig
import app.Modules.AsrListlist as GetPolicies
import app.Modules.build_service_policy as BuildService
import sqlite3

device = None
username = None
password = None
netconf_session = None
netmiko_session = None
get_interfaces = None
local_as = None
service_policies = None
qos = None
model = None


@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    global device, username, password, netconf_session, netmiko_session, model

    login_form = LoginForm(request.form)
    if 'login' in request.form:

        device = request.form['device']
        username = request.form['username']
        password = request.form['password']

        if device and username and password:

            # Attempt to create connection objects. Must have both to get to homepage
            netconf_session = ConnectWith.create_netconf_connection(request.form['username'], request.form['password'],
                                                                    request.form['device'])
            netmiko_session = ConnectWith.creat_netmiko_connection(request.form['username'], request.form['password'],
                                                                   request.form['device'])
            model = GetInfo.get_device_model(netmiko_session)

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
                return redirect(url_for('base_blueprint.login'))
            else:
                return redirect(url_for('base_blueprint.get_routing'))

        return render_template('accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/logout')
def logout():
    """User logout and re-login"""

    logout_user()
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/routing')
def get_routing():
    """Gets all things routing, arp, interfaces, routing protocols"""

    global get_interfaces, local_as

    # Get data, render homepage with variables
    get_interfaces = GetInterfacesInfo.get_ip_interfaces(netconf_session)

    bgp_status = GetInfo.get_bgp_status(netmiko_session)
    local_as = bgp_status[1][0]

    ospf_status = GetInfo.get_ospf_status(netmiko_session)
    arp_table = GetInfo.get_arp(netmiko_session)

    return render_template('routing.html', interfaces=get_interfaces,
                           bgp=bgp_status[0], ospf=ospf_status, arp=arp_table, intial='yes')


@blueprint.route('/routing', methods=['POST'])
def table_refresh():
    """Used for table refreshes"""

    action = request.form.get('action')

    # Used for refreshing tables without page reload, return data to call wich is js/ajax
    if action == 'arp':
        clear = GetInfo.clear_arp(netmiko_session)
        return jsonify({'data': render_template('refresh_arp.html', arps=clear)})
    elif action == 'bgp':
        get_status = GetInfo.get_bgp_status(netmiko_session)
        return jsonify({'data': render_template('refresh_bgp.html', bgp=get_status[0])})
    elif action == 'ospf':
        get_status = GetInfo.get_ospf_status(netmiko_session)
        return jsonify({'data': render_template('refresh_ospf.html', ospf=get_status)})
    elif action == 'clearInt':
        clear = GetInfo.clear_counters(netmiko_session, request.form.get('interface'), netconf_session)
        return jsonify({'data': render_template('refresh_table.html', interfaces=clear)})
    elif action == 'routes':

        # ReAuth and get IOS-XE routing table
        routing_session = ConnectWith.creat_netmiko_connection(username, password, device)
        mydb = sqlite3.connect("app/Modules/ProjectRouting/Database/Routing")
        cursor = mydb.cursor()
        db_obj = DB.RoutingDatabase(mydb, cursor)
        IOSXE.RoutingIos(routing_session, db_obj, mydb, cursor)

        return jsonify({'data': render_template('get_routing.html', route_table=Db_queries.view_routes_ios(cursor))})


@blueprint.route('/qos')
def get_qos():
    """View Qos statistics"""

    global service_policies, qos

    qos = GetQos.get_interfaces(netconf_session)
    service_policies = GetPolicies.fetch_service_policy(netconf_session)

    return render_template('qos.html', interfaces=get_interfaces, interface_qos=qos)


@blueprint.route('/modify_qos/<interface>')
def configure_qos(interface):
    """Render QOS configuration/Form"""

    reformat_interface = interface.replace('%2f', '/')

    return render_template('modify_qos.html', interface=reformat_interface, policies=service_policies)


@blueprint.route('/modify_qos', methods=['POST'])
def apply_qos():
    """POST QOS configuration from form data"""

    find_int_num = [i for i in request.form.get("interface") if i not in string.ascii_letters]
    find_int_type = [i for i in request.form.get("interface") if i in string.ascii_letters]
    build_config = BuildService.build_policy(''.join(find_int_type), ''.join(find_int_num), request.form.get("direction"), request.form.get("servicePolicy"))
    status = SendConfig.send_configuration(netconf_session, build_config)

    if status == 'Success':
        interface_qos = GetQos.get_interfaces(netconf_session)
        return jsonify({'data': render_template('qos_table.html', interface_qos=interface_qos)})
    else:
        return jsonify({'data': render_template('config_failed.html', status=status)})


@blueprint.route('/add_bgp_neighbor')
def add_bgp_neighbors():
    """POST BGP configuration from form data"""

    prefix_lists = GetPolicies.fetch_prefix_list(netconf_session)
    route_maps = GetPolicies.fetch_route_maps(netconf_session)

    return render_template('add_bgp_neighbor.html', local_as=local_as, prefixes=prefix_lists, route_map=route_maps)


@blueprint.route('/add_bgp_neighbor', methods=['POST'])
def post_neighbor():
    """Get device Qos, render page"""

    build_neighbors = Build_bgp_config.Templates(request.form.get("localAs"))
    bgp_config = build_neighbors.build_neighbor(request.form.get("neighborId"),
                                                request.form.get("remoteAs"),
                                                model,
                                                policy=[request.form.get("softReconfig"),
                                                        request.form.get("direction"),
                                                        request.form.get("policy"),
                                                        request.form.get("nextHop")])
    status = SendConfig.send_configuration(netconf_session, bgp_config)

    if status == 'Success':
        get_status = GetInfo.get_bgp_status(netmiko_session)
        return jsonify({'data': render_template('bgp_neighbor_table.html', bgp=get_status[0])})
    else:
        return jsonify({'data': render_template('config_failed.html', status=status)})


@blueprint.route('/add_ospf_neighbor')
def add_ospf_neighbors():
    """Render OSPF configuration/Form"""

    return render_template('add_ospf_neighbor.html')


@blueprint.route('/add_ospf_neighbor', methods=['POST'])
def post_ospf_neighbor():
    """POST OSPF configuration from form data"""

    build_neighbors = Build_ospf_config.Templates(request.form.get("process"))
    ospf_config = build_neighbors.build_neighbor(request.form.get("neighbor"),
                                                 request.form.get("wildcard"),
                                                 request.form.get("area"))
    status = SendConfig.send_configuration(netconf_session, ospf_config)

    if status == 'Success':
        get_status = GetInfo.get_ospf_status(netmiko_session)
        return jsonify({'data': render_template('ospf_neighbor_table.html', ospf=get_status)})
    else:
        return jsonify({'data': render_template('config_failed.html', status=status)})

