"""Collection of classes and funtion to write to SQL database"""

from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import time

engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/XEOps_3', pool_size=15000, echo=True)
Session = sessionmaker(bind=engine)
session = Session()


def db_commit():
    """Commit device information to DataBase"""
    try:
        session.commit()
    except InvalidRequestError:
        session.rollback()
    except IntegrityError:
        pass
    finally:
        session.close()


def copy_db_table(device):
    """Delete all rows in table, not the table itself"""

    for i in Base.metadata.tables.keys():
        front_end_table = i.replace('_back_end', '_front_end')

        if i == 'devicefacts_back_end':
            session.execute(f'DELETE FROM public.{front_end_table} WHERE unique_id=\'' + device + '\'')
        elif i != 'routeingtable_back_end':
            session.execute(f'DELETE FROM public.{front_end_table} WHERE id=\'' + device + '\'')
        db_commit()

        if i == 'devicefacts_back_end':
            session.execute(
                f'INSERT INTO public.{front_end_table} SELECT * FROM {i} WHERE unique_id=\'' + device + '\'')
        elif i != 'routeingtable_back_end':
            session.execute(f'INSERT INTO public.{front_end_table} SELECT * FROM {i} WHERE id=\'' + device + '\'')

        db_commit()


def copy_routing_table(device):
    """Delete all rows in table, not the table itself"""

    for i in Base.metadata.tables.keys():
        front_end_table = i.replace('_back_end', '_front_end')

        if i == 'routingtable_back_end':
            session.execute(f'DELETE FROM public.{front_end_table} WHERE id=\'' + device + '\'')
            db_commit()
            session.execute(f'INSERT INTO public.{front_end_table} SELECT * FROM {i} WHERE id=\'' + device + '\'')
            db_commit()


def delete_rows(table, column_id):
    """Delete all rows in table, not the table itself"""

    session.execute(f'DELETE FROM public.{table} WHERE id=\'' + column_id + '\'')
    db_commit()


def update_ip_interface_table(host, interface, ip_mac, admin, operational, speed, last_change, in_octets, out_octets):
    """Insert interface row in to table"""

    info = Interfaces(unique_id=f'{host}|{interface}', id=host, interface=interface, ip_mac=ip_mac, admin=admin,
                      operational=operational, speed=speed, last_change=last_change, in_octets=in_octets,
                      out_octets=out_octets, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_hsrp_table(host, interface, group, priority, preempt, state, active, standby, vip):
    """Insert interface row in to table"""

    info = Hsrp(unique_id=f'{host}|{vip}', id=host, interface=interface, group=group, priority=priority,
                preempt=preempt, state=state, active=active, standby=standby, vip=vip, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_arp_table(host, protocol, address, age, mac, ep_type, interfaces):
    """Insert arp entries row in to table"""

    info = Arp(unique_id=f'{host}|{address}', id=host, protocol=protocol, address=address, age=age, mac=mac,
               ep_type=ep_type, interfaces=interfaces, query_time=time.ctime())

    session.add(info)
    db_commit()


def update_vlan_table(host, vlan_id, vlan_prio, name, status, ports):
    """Insert vlans row in to table"""

    info = Vlans(unique_id=f'{host}|{vlan_id}', id=host, vlan_id=vlan_id, vlan_prio=vlan_prio, name=name,
                 status=status, ports=ports, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_mac_arp_table(host, vlan, address, ep_type, interface, ip, ip_interface):
    """Insert mac_arp row in to table"""

    info = ArpMac(unique_id=f'{host}|{address + vlan}', id=host, vlan=vlan, address=address + vlan, ep_type=ep_type,
                  interface=interface, ip=ip, ip_interface=ip_interface, query_time=time.ctime())

    session.add(info)
    db_commit()


def update_cdp_table(host, neighbor, local_port, remote_port):
    """Insert cdp row in to table"""

    info = Cdp(unique_id=f'{host}|{local_port}', id=host, neighbor=neighbor, local_port=local_port,
               remote_port=remote_port, query_time=time.ctime())

    session.add(info)
    db_commit()


def update_trunks_table(host, interface, vlans, admin, operational):
    """Insert trunk row into table"""

    info = Trunks(unique_id=f'{host}|{interface}', id=host, interface=interface, vlans=vlans, admin=admin,
                  operational=operational, query_time=time.ctime())

    session.add(info)
    db_commit()


def update_pochannel_table(host, interface, group, mode, admin, operational):
    """Insert port-channel row into table"""

    info = PoChannels(unique_id=f'{host}|{interface}', id=host, interface=interface, group=group, mode=mode,
                      admin=admin, operational=operational, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_bgp_table(host, neighbor, auto_sys, uptime, prefixes, local_as):
    """Insert bgp row into table"""

    info = Bgp(unique_id=f'{host}|{neighbor}', id=host, neighbor=neighbor, auto_sys=auto_sys, uptime=uptime,
               prefixes=prefixes, local_as=local_as, query_time=time.ctime())

    session.add(info)
    db_commit()


def update_ospf_table(host, neighbor, state, address, interface):
    """Insert OSPF row into table"""

    info = Ospf(unique_id=f'{host}|{neighbor}', id=host, neighbor=neighbor, state=state, address=address,
                interface=interface, query_time=time.ctime())

    session.add(info)
    db_commit()


def update_access_interfaces_table(host, interface, description, status, vlan, duplex, speed):
    """Insert access interface row into table"""

    info = AccessInterfaces(unique_id=f'{host}|{interface}', id=host, interface=interface, vlan=vlan,
                            description=description, status=status, duplex=duplex, speed=speed,
                            query_time=time.ctime())
    session.add(info)
    db_commit()


def update_spann_tree_table(host, vlan, root_prio, root_id, root_cost, root_port):
    """Insert spanning tree row into table"""

    info = SpanningTree(unique_id=f'{host}|{vlan}', id=host, vlan=vlan, root_cost=root_cost, root_port=root_port,
                        root_id=root_id, root_prio=root_prio, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_qos_table(host, interface, policy_name, direction, queue_name, rate, bytes, packets, out_bytes, out_packets,
                     drop_packets, drop_bytes, wred_drops_pkts, wred_drop_bytes):
    """Insert qos row into table"""

    query = session.query(InterfaceQos).filter(InterfaceQos.unique_id.like(f'{host}|{interface}|{rate}|{queue_name}')).count()

    if query == 0:
        info = InterfaceQos(unique_id=f'{host}|{interface}|{rate}|{queue_name}', id=host, interface=interface,
                            policy_name=policy_name, direction=direction, queue_name=queue_name, rate=rate, bytes=bytes,
                            packets=packets,
                            out_bytes=out_bytes, out_packets=out_packets, drop_packets=drop_packets,
                            drop_bytes=drop_bytes,
                            wred_drops_pkts=wred_drops_pkts, wred_drop_bytes=wred_drop_bytes,
                            query_time=time.ctime())
        session.add(info)
        db_commit()


def update_device_facts(host, serial, model, uptime, software, username, password, ssh_port, netconf_port):
    """Insert device facts row into table"""

    query = session.query(DeviceFacts).filter(DeviceFacts.unique_id.like(host)).count()
    no_db_entry = None

    if query == 0:

        no_db_entry = 'Device Not Found'
        info = DeviceFacts(unique_id=host, serial=serial, model=model, uptime=uptime, software=software,
                           username=username, password=password, ssh_port=ssh_port, netconf_port=netconf_port,
                           query_time=time.ctime())
        session.add(info)

    else:
        query = session.query(DeviceFacts).filter_by(unique_id=host).first()
        query.serial = serial
        query.model = model
        query.uptime = uptime
        query.software = software
        query.username = username
        query.password = password
        query.ssh_port = ssh_port
        query.netconf_port = netconf_port
        query.query_time = time.ctime()

    db_commit()

    return no_db_entry


def update_unassigned_interfaces(host, interface):
    """Insert unassigned interface row into table"""

    info = UnassignedInterfaces(unique_id=f'{host}|{interface}', id=host, interface=interface,
                                query_time=time.ctime())
    session.add(info)
    db_commit()


def update_vrfs_table(host, vrf):
    """Insert vrf row into table"""

    info = Vrfs(unique_id=f'{host}|{vrf}', id=host, vrf=vrf, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_ospf_process_table(host, process):
    """Insert ospf process row into table"""

    info = OspfProcess(unique_id=f'{host}|{process}', id=host, process=process, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_prefix_table(host, name, seq, action, ge, le):
    """Insert prefix row into table"""

    info = PrefixList(unique_id=f'{host}|{name}|{seq}', id=host, name=name, action=action, seq=seq, ge=ge, le=le,
                      query_time=time.ctime())
    session.add(info)
    db_commit()


def update_route_maps(host, name):
    """Insert route_map row into table"""

    info = RouteMaps(unique_id=f'{host}|{name}', id=host, name=name, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_configurations(host, username, config, config_category):
    """Insert configuration row into table"""

    info = Configurations(unique_id=f'{host}|{time.strftime("%X %x %Z")}', id=host, username=username,
                          config_category=config_category, query_time=time.ctime())
    session.add(info)
    db_commit()


def update_routing_table(host, vrf, prefix, protocol, admin_distance, metric, next_hops, interfaces, tag, age):
    """Inserts routes in to table"""

    query = session.query(RoutingTable).filter(RoutingTable.unique_id.like(f'{host}|{prefix}|{vrf}')).count()

    if query == 0:
        info = RoutingTable(unique_id=f'{host}|{prefix}|{vrf}', id=host, vrf=vrf, prefix=prefix, protocol=protocol,
                            admin_distance=admin_distance,
                            metric=metric, next_hops=next_hops, interfaces=interfaces, tag=tag, age=age,
                            query_time=time.ctime())
        session.add(info)
        db_commit()


def update_ospf_router_table(host, process, router_id, neigh_router_id, route_type, cost, nexthop, interface,
                             router_type, area, spf):
    """Inserts routes in to table"""
    query = session.query(OspfRouterTable).filter(OspfRouterTable.unique_id.like(f'{host}|{neigh_router_id}')).count()

    if query == 0:
        info = OspfRouterTable(unique_id=f'{host}|{neigh_router_id}', id=host, process=process, router_id=router_id,
                               neigh_router_id=neigh_router_id, route_type=route_type, cost=cost, nexthop=nexthop,
                               interface=interface,
                               router_type=router_type, area=area, spf=spf, query_time=time.ctime())

        session.add(info)
        db_commit()


def update_dmvpn_table(host, peer_nbma, peer_address, state, updn_time, attrib):
    """Inserts dmvpn data in to table"""

    info = DmvpnTable(unique_id=f'{host}|{peer_nbma}', id=host,
                      peer_nbma=peer_nbma, peer_address=peer_address, state=state, updn_time=updn_time,
                      attrib=attrib, query_time=time.ctime())

    session.add(info)
    db_commit()


def update_dmvpn_count(host, interface, router_type, peer_count):
    """Inserts dmvpn data in to table"""

    info = DmvpnCountTable(unique_id=f'{host}|{interface}', id=host, interface=interface, router_type=router_type,
                           peer_count=peer_count, query_time=time.ctime())

    session.add(info)
    db_commit()


def update_dmvpn_interfaces(host, interface, ip_add, tunnel_source, tunnel_mode, network_id, holdtime, profile,
                            nhrp_shortcut, nhrp_redirect):
    """Inserts dmvpn data in to table"""

    info = DmvpnInterfacesTable(unique_id=f'{host}|{ip_add}', id=host, interface=interface, ip_add=ip_add,
                                tunnel_source=tunnel_source,
                                tunnel_mode=tunnel_mode, network_id=network_id, holdtime=holdtime, profile=profile,
                                nhrp_shortcut=nhrp_shortcut,
                                nhrp_redirect=nhrp_redirect, query_time=time.ctime())

    session.add(info)
    db_commit()


Base = declarative_base()


#                                                                                           |
# Called by the caller "above funtions" for querying and updating database ROWS: 237 - 434  |
# Database tables will also be create using row 414                                         v
#                                                                                           v

class Interfaces(Base):
    """"""

    __tablename__ = "interfaces_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    interface = Column(String)
    ip_mac = Column(String)
    admin = Column(String)
    operational = Column(String)
    speed = Column(String)
    last_change = Column(String)
    in_octets = Column(String)
    out_octets = Column(String)
    query_time = Column(String)


class Arp(Base):
    """"""

    __tablename__ = "arp_back_end"

    unique_id = Column(String(50), primary_key=True)
    address = Column(String)
    protocol = Column(String)
    id = Column(String)
    age = Column(String)
    mac = Column(String)
    ep_type = Column(String)
    interfaces = Column(String)
    query_time = Column(String)


class Vlans(Base):
    """"""

    __tablename__ = "vlans_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    vlan_id = Column(String)
    vlan_prio = Column(String)
    name = Column(String)
    status = Column(String)
    ports = Column(String(300))
    query_time = Column(String)


class ArpMac(Base):
    """"""

    __tablename__ = "arpmac_back_end"

    unique_id = Column(String(50), primary_key=True)
    address = Column(String)
    id = Column(String)
    vlan = Column(String)
    ep_type = Column(String)
    interface = Column(String)
    ip = Column(String)
    ip_interface = Column(String)
    query_time = Column(String)


class Cdp(Base):
    """"""

    __tablename__ = "cdp_back_end"

    unique_id = Column(String(50), primary_key=True)
    local_port = Column(String)
    id = Column(String)
    neighbor = Column(String)
    remote_port = Column(String)
    query_time = Column(String)


class Trunks(Base):
    """"""

    __tablename__ = "trunks_back_end"

    unique_id = Column(String(50), primary_key=True)
    interface = Column(String)
    id = Column(String)
    vlans = Column(String)
    admin = Column(String)
    operational = Column(String)
    query_time = Column(String)


class PoChannels(Base):
    """"""

    __tablename__ = "pochannels_back_end"

    unique_id = Column(String(50), primary_key=True)
    interface = Column(String)
    id = Column(String)
    group = Column(String)
    mode = Column(String)
    admin = Column(String)
    operational = Column(String)
    query_time = Column(String)


class Bgp(Base):
    """"""

    __tablename__ = "bgp_back_end"

    unique_id = Column(String(50), primary_key=True)
    neighbor = Column(String)
    id = Column(String)
    auto_sys = Column(String)
    uptime = Column(String)
    prefixes = Column(String)
    local_as = Column(String)
    query_time = Column(String)


class Ospf(Base):
    """"""

    __tablename__ = "ospf_back_end"

    unique_id = Column(String(50), primary_key=True)
    neighbor = Column(String)
    id = Column(String)
    state = Column(String)
    address = Column(String)
    interface = Column(String)
    query_time = Column(String)


class AccessInterfaces(Base):
    """"""

    __tablename__ = "accessinterfaces_back_end"

    unique_id = Column(String(50), primary_key=True)
    interface = Column(String)
    id = Column(String)
    vlan = Column(String)
    description = Column(String)
    status = Column(String)
    duplex = Column(String)
    speed = Column(String)
    query_time = Column(String)


class SpanningTree(Base):
    """"""

    __tablename__ = "spanningtree_back_end"

    unique_id = Column(String(50), primary_key=True)
    vlan = Column(String)
    id = Column(String)
    root_prio = Column(String)
    root_id = Column(String)
    root_cost = Column(String)
    root_port = Column(String)
    query_time = Column(String)


class InterfaceQos(Base):
    """"""

    __tablename__ = "interfaceqos_back_end"

    unique_id = Column(String(200), primary_key=True)
    interface = Column(String)
    id = Column(String)
    policy_name = Column(String)
    direction = Column(String)
    queue_name = Column(String)
    rate = Column(String)
    bytes = Column(String)
    packets = Column(String)
    out_bytes = Column(String)
    out_packets = Column(String)
    drop_packets = Column(String)
    drop_bytes = Column(String)
    wred_drops_pkts = Column(String)
    wred_drop_bytes = Column(String)
    bytes = Column(String)
    query_time = Column(String)


class DeviceFacts(Base):
    """"""

    __tablename__ = "devicefacts_back_end"

    unique_id = Column(String(50), primary_key=True)
    serial = Column(String)
    model = Column(String)
    uptime = Column(String)
    software = Column(String)
    username = Column(String)
    password = Column(String)
    ssh_port = Column(Integer)
    netconf_port = Column(Integer)
    query_time = Column(String)


class UnassignedInterfaces(Base):
    """"""

    __tablename__ = "unassignedinterfaces_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    interface = Column(String)
    query_time = Column(String)


class Vrfs(Base):
    """"""

    __tablename__ = "vrfs_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    vrf = Column(String)
    query_time = Column(String)


class OspfProcess(Base):
    """"""

    __tablename__ = "ospfprocess_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    process = Column(String)
    query_time = Column(String)


class PrefixList(Base):
    """"""

    __tablename__ = "prefixlist_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    name = Column(String)
    action = Column(String)
    seq = Column(String)
    ge = Column(String)
    le = Column(String)
    query_time = Column(String)


class RouteMaps(Base):
    """"""

    __tablename__ = "routemaps_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    name = Column(String)
    query_time = Column(String)


class Configurations(Base):
    """"""

    __tablename__ = "configurations_back_end"

    unique_id = Column(String(75), primary_key=True)
    id = Column(String)
    username = Column(String)
    config = Column(String(1000))
    config_category = Column(String)
    query_time = Column(String)


class RoutingTable(Base):
    """"""

    __tablename__ = "routingtable_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    vrf = Column(String)
    prefix = Column(String)
    protocol = Column(String)
    admin_distance = Column(String)
    metric = Column(String)
    next_hops = Column(String)
    interfaces = Column(String)
    tag = Column(String)
    age = Column(String)
    query_time = Column(String)


class Hsrp(Base):
    """"""

    __tablename__ = "hsrp_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    interface = Column(String)
    group = Column(String)
    priority = Column(String)
    preempt = Column(String)
    state = Column(String)
    active = Column(String)
    standby = Column(String)
    vip = Column(String)
    query_time = Column(String)


class OspfRouterTable(Base):
    """"""

    __tablename__ = "ospfrouters_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    process = Column(String)
    router_id = Column(String)
    neigh_router_id = Column(String)
    route_type = Column(String)
    cost = Column(String)
    nexthop = Column(String)
    interface = Column(String)
    router_type = Column(String)
    area = Column(String)
    spf = Column(String)
    query_time = Column(String)


class DmvpnTable(Base):
    """"""

    __tablename__ = "dmvpn_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    peer_nbma = Column(String)
    peer_address = Column(String)
    state = Column(String)
    updn_time = Column(String)
    attrib = Column(String)
    query_time = Column(String)


class DmvpnCountTable(Base):
    """"""

    __tablename__ = "dmvpncount_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    interface = Column(String)
    router_type = Column(String)
    peer_count = Column(String)
    query_time = Column(String)


class DmvpnInterfacesTable(Base):
    """"""

    __tablename__ = "dmvpninterfaces_back_end"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    interface = Column(String)
    ip_add = Column(String)
    tunnel_source = Column(String)
    tunnel_mode = Column(String)
    network_id = Column(String)
    holdtime = Column(String)
    profile = Column(String)
    nhrp_shortcut = Column(String)
    nhrp_redirect = Column(String)
    query_time = Column(String)


# Create Tables from above Classes
Base.metadata.create_all(engine)
