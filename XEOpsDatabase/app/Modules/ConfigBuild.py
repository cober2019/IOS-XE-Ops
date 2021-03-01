from jinja2 import Template
import app.Modules.connection as ConnectWith
import app.Modules.ConfigValidation as ValidateConfig
import app.Database.DbOperations as DbOps
import app.Database.DatabaseQueries as QueryDbFor
import os
import napalm
import string

# File paths for jinja configuration files. Get current directory and replace with config directory, add filename
build_vlan_path = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/add_vlan.j2'
build_int_path = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/add_modiy_interface.j2'
build_ospf_path = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/build_ospf'
build_bgp_path = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/build_bgp'
build_qos_path = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/build_qos_int'
build_custom_path = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/custom'
build_access_int_path = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/modify_add_access_interface.j2'
build_vlan_to_trunk = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/add_vlan_to_trunk.j2'
build_link_to_pochan = os.path.dirname(__file__).replace("Modules", "ConfigTemplates") + '/add_link_pochan.j2'


def build_vlan(id, name, action):
    """Build vlan config using Jinja2"""

    with open(build_vlan_path) as vlan_file:
        build_vlan_template = Template(vlan_file.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        vlan_config_j2 = build_vlan_template.render(vlan_id=id, vlan_name=name, action=action)

    return vlan_config_j2

def build_porch_link(interface, channel_group, mode):
    """Build/Assign interface to portchannel using Jinja2"""

    with open(build_link_to_pochan) as pochann_file:
        build_pochann_template = Template(pochann_file.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        poch_config_j2 = build_pochann_template.render(channel_group=channel_group, interface=interface, mode=mode)

    return poch_config_j2

def build_interface(int, ip, mask, status, vrf, descr, switchport):
    """Build interface config using Jinja2"""

    with open(build_int_path) as interface_file:
        build_vlan_template = Template(interface_file.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        int_config_j2 = build_vlan_template.render(int=int, ip=ip, mask=mask, status=status, vrf=vrf, descr=descr, switchport=switchport)
        
    return int_config_j2


def build_access_interface(interface, vlan, descr, status, voice_vlan):
    """Build interface config using Jinja2"""

    with open(build_access_int_path) as access_interface_file:
        build_access_int_template = Template(access_interface_file.read(), keep_trailing_newline=True, trim_blocks=True,
                                       lstrip_blocks=True)
        access_int_config_j2 = build_access_int_template.render(interface=interface, vlan=vlan, descr=descr, status=status,
                                                                voice_vlan=voice_vlan)

    return access_int_config_j2

def build_ospf(proccess, network, wildcard, area):
    """Build ospf config using Jinja2"""

    with open(build_ospf_path) as ospf_file:
        build_ospf_template = Template(ospf_file.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        ospf_config_j2 = build_ospf_template.render(proccess=proccess, network=network, wildcard=wildcard, area=area)

    return ospf_config_j2

def build_interface_qos(interface, policy, direction):
    """Build ospf config using Jinja2"""

    with open(build_qos_path) as qos_file:
        build_int_qos_template = Template(ospf_file.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        int_qos_config_j2 = build_int_qos_template.render(interface=interface, policy=policy, direction=direction)

    return int_qos_config_j2

def build_bgp(neighbor, remote_as, soft_reconfig, next_hop, policy):
    """Build BGP config using Jinja2"""

    with open(build_bgp_path) as bgp_file:
        build_bgp_template = Template(bgp_file.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        bgp_config_j2 = build_bgp_template.render(neighbor=neighbor, remote_as=remote_as, soft_reconfig=soft_reconfig,
                                                  next_hop=next_hop, policy=policy)
    return bgp_config_j2

def build_add_trunk_vlan(interface, vlan, action):
    """Build BGP config using Jinja2"""

    with open(build_vlan_to_trunk) as trunk_file:
        build_vlan_trunk_template = Template(trunk_file.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        vlan_trunk_config_j2 = build_vlan_trunk_template.render(interface=interface, vlan=vlan, action=action)

    return vlan_trunk_config_j2

def build_custom_config(config):
    """Build BGP config using Jinja2"""

    with open(build_custom_path) as custom_file:
        build_custom_template = Template(custom_file.read(), keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        custom_j2 = build_custom_template.render(config=config)

    return custom_j2

def send_config(host, username, password, config):
    """Send Jinja config using Napalm"""

    print(config)
    status = None

    try:
        driver = napalm.get_network_driver('ios')
        device_conn = driver(host, username, password)
        device_conn.open()
        device_conn.load_merge_candidate(config=config)
        test = device_conn.commit_config()
        device_conn.close()
        status = 'success'
    except napalm.base.exceptions.MergeConfigException:
        status = 'fail'
    except napalm.base.exceptions.CommandErrorException:
        status = 'fail'
    except napalm.base.exceptions.ConnectionException:
        status = 'fail'

    return status

def send_config_cli(host, username, password, config):
    """Send Jinja config using netmiko. Used for configs napalm wont send"""

    # Create netconfi session
    session = ConnectWith.creat_netmiko_connection(username, password, host, 22)

    try:
        session.send_command('config t\n', expect_string='#')
        for i in config.splitlines():
            print(i)
            session.send_command(i + '\n', expect_string='#')
            status = 'custom_success'
    except:
        status = 'custom_fail'

    return status

def parse_int_form(form, device, password, username):
    """Parse, build, send info for interface configuration"""

    ip, mask, status, descr, vrf, switchport= None, None, None, None, None, None

    if not form.get('newIntCustomForm'):
        if form.get('ip') and form.get('mask'):
            ip = form.get('ip')
            mask = form.get('mask')
        if form.get('status'):
            status = form.get('status')
        if form.get('description'):
            descr = form.get('description')
        if form.get('vrf'):
            vrf = form.get('vrf')
        if form.get('negotiation'):
            negotiation = form.get('negotiation')
        if form.get('vlan'):
            negotiation = form.get('negotiation')
        if form.get('switchport'):
            switchport = form.get('switchport')

        # Convert interface number back to slashes from %2f
        int_num = [i for i in form.get("interface") if i not in string.ascii_letters]
        int_type = [i for i in form.get("interface") if i in string.ascii_letters]

        # Validate interface perameters
        validation = ValidateConfig.validate_interface(''.join(int_type) + ''.join(int_num), ip, mask, status, vrf,
                                                       descr, QueryDbFor.query_interfaces(device))
        config = build_interface(''.join(int_type) + ''.join(int_num), ip, mask, status, vrf, descr, switchport)
        # If validation passes which is 0, send config, update DB
        if validation == 0:
            status = send_config(device, username, password, config)
            DbOps.update_configurations(device, username, config, "Modify/Add Interface")
    else:
        status = send_config_cli(device, username, password, form.get('newIntCustomForm'))
        DbOps.update_configurations(device, username, form.get('newIntCustomForm'), "Modify/Add Interface")

    return status

def parse_access_int_form(form, device, password, username):
    """Parse, build, send info for access interface configuration"""

    vlan, descr, status, voice_vlan = None, None, None, None

    if not form.get('vlanCustomForm'):
        if form.get('status'):
            status = form.get('status')
        if form.get('description'):
            descr = form.get('description')
        if form.get('vlan'):
            vlan = form.get('vlan')
        if form.get('voiceVlan') != 'None':
            voice_vlan = form.get('voiceVlan')
        else:
            voice_vlan = None

        # Convert interface number back to slashes from %2f
        int_num = [i for i in form.get("interface") if i not in string.ascii_letters]
        int_type = [i for i in form.get("interface") if i in string.ascii_letters]

        # Build and send config, updated DB
        status = send_config(device, username, password, config)
        DbOps.update_configurations(device, username, config, 'Modify Access Interface')
    else:
        status = send_config_cli(device, username, password, form.get('vlanCustomForm'))
        DbOps.update_configurations(device, username, form.get('vlanCustomForm'), 'Modify Access Interface')

    return status

def parse_add_vlan_form(form, device, password, username):
    """Parse, build, send info for vlan configuration"""

    if not form.get('vlanCustomForm'):
        config = build_vlan(form.get('vlanId'), form.get('vlanName'), form.get('action'))
        status = send_config_cli(device, username, password, config)
        DbOps.update_configurations(device, username, config, 'Vlan')
    else:
        status = send_config_cli(device, username, password, form.get('vlanCustomForm'))
        DbOps.update_configurations(device, username, form.get('vlanCustomForm'), 'Vlan')

    return status

def parse_trunk_interface(form, device, password, username):
    """Parse, build, send info for trunk configuration"""

    if form.get("trunkCustomForm"):
        status = send_config_cli(device, username, password, form.get("trunkCustomForm"))
        DbOps.update_configurations(device, username, form.get("trunkCustomForm"), 'Modify Trunk')
    else:
        config = build_add_trunk_vlan(''.join(int_type) + ''.join(int_num), form.get('vlan'), form.get('action'))
        # Convert interface number back to slashes from %2f
        int_num = [i for i in form.get("interface") if i not in string.ascii_letters]
        int_type = [i for i in form.get("interface") if i in string.ascii_letters]
        status = send_config(device, username, password, config)
        DbOps.update_configurations(device, username, config, 'Modify Trunk')

    return status

def parse_routing_config(form, device, password, username):
    """Parse, build, and send new routing configuration"""

    # Proccess for data from input fields
    if request.form.get("process") is not None:
        config = BuildConfig.build_ospf(request.form.get("process"), request.form.get("neighbor"),
                                        request.form.get("wildcard"), request.form.get("area"))
        status = BuildConfig.send_config(device, username, password, config)
        DbOps.update_configurations(device, username, config, 'Ospf')

    elif request.form.get("remoteAs") is not None:
        config = BuildConfig.build_bgp(request.form.get("neighborId"), request.form.get("remoteAs"),
                                       request.form.get("softReconfig"), request.form.get("nextHop"),
                                       policy=[request.form.get("direction"), request.form.get("policy")])
        status = BuildConfig.send_config(device, username, password, config)
        DbOps.update_configurations(device, username, config, 'Bgp')

    # Proccess for data from input field TEXT AREA
    if request.form.get("bgpCustomForm") is not None:
        status = BuildConfig.send_config(device, username, password, request.form.get("bgpCustomForm"))
        DbOps.update_configurations(device, username, request.form.get("bgpCustomForm"), 'Bgp')

    elif request.form.get("ospfCustomForm") is not None:
        status = BuildConfig.send_config(device, username, password, request.form.get("ospfCustomForm"))
        DbOps.update_configurations(device, username, request.form.get("ospfCustomForm"), 'Ospf')

    return status

def parse_poch_interface(form, mode, device, password, username):
    """Parse, build, send info for trunk configuration"""

    # Convert interface number back to slashes from %2f

    if form.get("pochCustomForm"):
        status = send_config_cli(device, username, password, form.get('pochCustomForm'))
        DbOps.update_configurations(device, username, form.get('pochCustomForm'), 'Add Link to Portchannel')
    else:
        int_num = [i for i in form.get("interface") if i not in string.ascii_letters]
        int_type = [i for i in form.get("interface") if i in string.ascii_letters]
        config = build_porch_link(''.join(int_type) + ''.join(int_num), form.get('pochannel'), mode)
        status = send_config(device, username, password, config)
        DbOps.update_configurations(device, username, config, 'Add Link to Portchannel')

    return status