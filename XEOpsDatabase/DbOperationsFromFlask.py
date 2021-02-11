from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

engine = create_engine('mssql+pymssql://testuser:4321@192.168.86.248:1443/XEOps', echo=True)
Session = sessionmaker(bind=engine)
session = Session()


def update_ip_interface_table(host, interface, ip_mac, admin, operational, speed, last_change, in_octets, out_octets):
    """Insert interface row in to table"""

    query = session.query(Interfaces).filter(Interfaces.unique_id.like(f'{host}|{interface}')).count()

    if query == 0:
        info = Interfaces(unique_id=f'{host}|{interface}', id=host, interface=interface, ip_mac=ip_mac, admin=admin,
                          operational=operational, speed=speed, last_change=last_change, in_octets=in_octets,
                          out_octets=out_octets)
        session.add(info)
    else:
        query = session.query(Arp).filter_by(unique_id=f'{host}|{interface}').first()
        query.id = host
        query.interface = interface
        query.ip_mac = ip_mac
        query.admin = admin
        query.operational = operational
        query.speed = speed
        query.last_change = last_change
        query.in_octets = in_octets
        query.out_octets = out_octets

    session.commit()


def update_arp_table(host, protocol, address, age, mac, type, interfaces):
    """Insert arp entries row in to table"""

    query = session.query(Arp).filter(Arp.unique_id.like(f'{host}|{address}')).count()

    if query == 0:
        info = Arp(unique_id=f'{host}|{address}', id=host, protocol=protocol, address=address, age=age, mac=mac,
                   type=type, interfaces=interfaces)
        session.add(info)
    else:
        query = session.query(Arp).filter_by(unique_id=f'{host}|{address}').first()
        query.address = address
        query.protocol = protocol
        query.id = host
        query.age = age
        query.mac = mac
        query.type = type
        query.interfaces = interfaces

    session.commit()


def update_vlan_table(host, vlan_id, vlan_prio, name, status, ports):
    """Insert vlans row in to table"""

    query = session.query(Vlans).filter(Vlans.unique_id.like(host)).count()

    if query == 0:
        info = Vlans(unique_id=f'{host}|{vlan_id}', id=host, vlan_id=vlan_id, vlan_prio=vlan_prio, name=name,
                     status=status, ports=ports)
        session.add(info)
    else:
        query = session.query(Vlans).filter_by(unique_id=f'{host}|{vlan_id}').first()
        query.id = host
        query.vlan_id = vlan_id
        query.vlan_prio = vlan_prio
        query.name = name
        query.status = status
        query.ports = ports

    session.commit()


def update_mac_arp_table(host, vlan, address, type, interface, ip, ip_interface):
    """Insert mac_arp row in to table"""

    query = session.query(ArpMac).filter(ArpMac.unique_id.like(f'{host}|{address + vlan}')).count()

    if query == 0:
        info = ArpMac(unique_id=f'{host}|{address + vlan}', id=host, vlan=vlan, address=address + vlan, type=type,
                      interface=interface, ip=ip, ip_interface=ip_interface)
        session.add(info)
    else:
        query = session.query(ArpMac).filter_by(unique_id=f'{host}|{address + vlan}').first()
        query.address = address
        query.id = host
        query.vlan = vlan
        query.type = type
        query.interface = interface
        query.ip = ip
        query.ip_interface = ip_interface

    session.commit()


def update_cdp_table(host, neighbor, local_port, remote_port):
    """Insert cdp row in to table"""

    query = session.query(Cdp).filter(Cdp.unique_id.like(f'{host}|{local_port}')).count()

    if query == 0:
        info = Cdp(unique_id=f'{host}|{local_port}', id=host, neighbor=neighbor, local_port=local_port,
                   remote_port=remote_port)
        session.add(info)
    else:
        query = session.query(Cdp).filter_by(unique_id=f'{host}|{local_port}').first()
        query.local_port = local_port
        query.id = host
        query.neighbor = neighbor
        query.remote_port = remote_port

    session.commit()


def update_trunks_table(host, interface, vlans, admin, operational):
    """Insert trunk row into table"""

    query = session.query(Trunks).filter(Trunks.unique_id.like(f'{host}|{interface}')).count()

    if query == 0:
        info = Trunks(unique_id=f'{host}|{interface}', id=host, interface=interface, vlans=vlans, admin=admin,
                      operational=operational)
        session.add(info)
    else:
        query = session.query(Trunks).filter_by(unique_id=f'{host}|{interface}').first()
        query.interface = interface
        query.id = host
        query.vlans = vlans
        query.admin = admin
        query.operational = operational

    session.commit()


def update_pochannel_table(host, interface, group, mode, admin, operational):
    """Insert port-channel row into table"""

    query = session.query(PoChannels).filter(PoChannels.unique_id.like(f'{host}|{interface}')).count()

    if query == 0:
        info = PoChannels(unique_id=f'{host}|{interface}', id=host, interface=interface, group=group, mode=mode,
                          admin=admin, operational=operational)
        session.add(info)
    else:
        query = session.query(PoChannels).filter_by(unique_id=f'{host}|{interface}').first()
        query.interface = interface
        query.id = host
        query.group = group
        query.mode = mode
        query.admin = admin
        query.operational = operational

    session.commit()


def update_bgp_table(host, neighbor, auto_sys, uptime, prefixes, local_as):
    """Insert bgp row into table"""

    query = session.query(Bgp).filter(Bgp.unique_id.like(f'{host}|{neighbor}')).count()

    if query == 0:
        info = Bgp(unique_id=f'{host}|{neighbor}', id=host, neighbor=neighbor, auto_sys=auto_sys, uptime=uptime,
                   prefixes=prefixes, local_as=local_as)
        session.add(info)
    else:
        query = session.query(Bgp).filter_by(unique_id=f'{host}|{neighbor}').first()
        query.neighbor = neighbor
        query.id = host
        query.auto_sys = auto_sys
        query.uptime = uptime
        query.prefixes = prefixes
        query.local_as = local_as

    session.commit()


def update_ospf_table(host, neighbor, state, address, interface):
    """Insert OSPF row into table"""

    query = session.query(Ospf).filter(Ospf.unique_id.like(f'{host}|{neighbor}')).count()

    if query == 0:
        info = Ospf(unique_id=f'{host}|{neighbor}', id=host, neighbor=neighbor, state=state, address=address,
                    interface=interface)
        session.add(info)
    else:
        query = session.query(Ospf).filter_by(unique_id=f'{host}|{neighbor}').first()
        query.neighbor = neighbor
        query.id = host
        query.state = state
        query.address = address
        query.interface = interface

    session.commit()


def update_access_interfaces_table(host, interface, vlan, admin, operational):
    """Insert access interface row into table"""

    query = session.query(AccessInterfaces).filter(AccessInterfaces.unique_id.like(f'{host}|{interface}')).count()

    if query == 0:
        info = AccessInterfaces(unique_id=f'{host}|{interface}', id=host, interface=interface, vlan=vlan, admin=admin,
                                operational=operational)
        session.add(info)
    else:
        query = session.query(AccessInterfaces).filter_by(unique_id=f'{host}|{interface}').first()
        query.interface = interface
        query.id = host
        query.vlan = vlan
        query.admin = admin
        query.operational = operational

    session.commit()


def update_spann_tree_table(host, vlan, root_prio, root_id, root_cost, root_port):
    """Insert spanning tree row into table"""

    query = session.query(SpanningTree).filter(SpanningTree.unique_id.like(f'{host}|{vlan}')).count()

    if query == 0:
        info = SpanningTree(unique_id=f'{host}|{vlan}', id=host, vlan=vlan, root_cost=root_cost, root_port=root_port,
                            root_id=root_id, root_prio=root_prio)
        session.add(info)
    else:
        query = session.query(SpanningTree).filter_by(unique_id=f'{host}|{vlan}').first()
        query.vlan = vlan
        query.id = host
        query.root_prio = root_prio
        query.root_id = root_id
        query.root_cost = root_cost
        query.root_port = root_port

    session.commit()


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
                            wred_drops_pkts=wred_drops_pkts, wred_drop_bytes=wred_drop_bytes)
        session.add(info)
    else:
        query = session.query(InterfaceQos).filter_by(unique_id=f'{host}|{interface}|{rate}|{queue_name}').first()
        query.interface = interface
        query.id = host
        query.policy_name = policy_name
        query.direction = direction
        query.queue_name = queue_name
        query.rate = rate
        query.bytes = bytes
        query.packets = packets
        query.out_bytes = out_bytes
        query.out_packets = out_packets
        query.drop_packets = drop_packets
        query.drop_bytes = drop_bytes
        query.wred_drops_pkts = wred_drops_pkts
        query.wred_drop_bytes = wred_drops_pkts
        query.bytes = bytes

    session.commit()


def update_device_facts(host, serial, model, uptime, software, username, password):
    """Insert device facts row into table"""

    query = session.query(DeviceFacts).filter(DeviceFacts.unique_id.like(host)).count()
    no_db_entry = None

    if query == 0:

        no_db_entry = 'Device Not Found'
        info = DeviceFacts(unique_id=host, serial=serial, model=model, uptime=uptime, software=software,
                           username=username, password=password)
        session.add(info)
    else:
        query = session.query(DeviceFacts).filter_by(unique_id=host).first()
        query.serial = serial
        query.model = model
        query.uptime = uptime
        query.software = software
        query.username = username
        query.password = password

    session.commit()

    return no_db_entry


def update_unassigned_interfaces(host, interface):
    """Insert unassigned interface row into table"""

    query = session.query(UnassignedInterfaces).filter(UnassignedInterfaces.unique_id.like(f'{host}|{interface}')).count()

    if query == 0:
        info = UnassignedInterfaces(unique_id=f'{host}|{interface}', id=host, interface=interface)
        session.add(info)
    else:
        query = session.query(UnassignedInterfaces).filter_by(unique_id=f'{host}|{interface}').first()
        query.id = host
        query.interface = interface

    session.commit()


def update_vrfs_table(host, vrf):
    """Insert unassigned interface row into table"""

    query = session.query(Vrfs).filter(Vrfs.unique_id.like(f'{host}|{vrf}')).count()

    if query == 0:
        info = Vrfs(unique_id=f'{host}|{vrf}', id=host, vrf=vrf)
        session.add(info)
    else:
        query = session.query(Vrfs).filter_by(unique_id=f'{host}|{vrf}').first()
        query.id = host
        query.vrf = vrf

    session.commit()


def update_ospf_process_table(host, process):
    """Insert unassigned interface row into table"""

    query = session.query(OspfProcess).filter(OspfProcess.unique_id.like(f'{host}|{process}')).count()

    if query == 0:
        info = OspfProcess(unique_id=f'{host}|{process}', id=host, process=process)
        session.add(info)
    else:
        query = session.query(OspfProcess).filter_by(unique_id=f'{host}|{process}').first()
        query.process = host

    session.commit()


Base = declarative_base()


#                                                                                           |
# Called by the caller "above funtions" for querying and updating database ROWS: 237 - 434  |
# Database tables will also be create using row 414                                         v
#                                                                                           v

class Interfaces(Base):
    """"""

    __tablename__ = "Interfaces"

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


class Arp(Base):
    """"""

    __tablename__ = "Arp"

    unique_id = Column(String(50), primary_key=True)
    address = Column(String)
    protocol = Column(String)
    id = Column(String)
    age = Column(String)
    mac = Column(String)
    type = Column(String)
    interfaces = Column(String)


class Vlans(Base):
    """"""

    __tablename__ = "Vlans"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    vlan_id = Column(String)
    vlan_prio = Column(String)
    name = Column(String)
    status = Column(String)
    ports = Column(String)


class ArpMac(Base):
    """"""

    __tablename__ = "ArpMac"

    unique_id = Column(String(50), primary_key=True)
    address = Column(String)
    id = Column(String)
    vlan = Column(String)
    type = Column(String)
    interface = Column(String)
    ip = Column(String)
    ip_interface = Column(String)


class Cdp(Base):
    """"""

    __tablename__ = "Cdp"

    unique_id = Column(String(50), primary_key=True)
    local_port = Column(String)
    id = Column(String)
    neighbor = Column(String)
    remote_port = Column(String)


class Trunks(Base):
    """"""

    __tablename__ = "Trunks"

    unique_id = Column(String(50), primary_key=True)
    interface = Column(String)
    id = Column(String)
    vlans = Column(String)
    admin = Column(String)
    operational = Column(String)


class PoChannels(Base):
    """"""

    __tablename__ = "PoChannels"

    unique_id = Column(String(50), primary_key=True)
    interface = Column(String)
    id = Column(String)
    group = Column(String)
    mode = Column(String)
    admin = Column(String)
    operational = Column(String)


class Bgp(Base):
    """"""

    __tablename__ = "Bgp"

    unique_id = Column(String(50), primary_key=True)
    neighbor = Column(String)
    id = Column(String)
    auto_sys = Column(String)
    uptime = Column(String)
    prefixes = Column(String)
    local_as = Column(String)


class Ospf(Base):
    """"""

    __tablename__ = "Ospf"

    unique_id = Column(String(50), primary_key=True)
    neighbor = Column(String)
    id = Column(String)
    state = Column(String)
    address = Column(String)
    interface = Column(String)


class AccessInterfaces(Base):
    """"""

    __tablename__ = "AccessInterfaces"

    unique_id = Column(String(50), primary_key=True)
    interface = Column(String)
    id = Column(String)
    vlan = Column(String)
    admin = Column(String)
    operational = Column(String)


class SpanningTree(Base):
    """"""

    __tablename__ = "SpanningTree"

    unique_id = Column(String(50), primary_key=True)
    vlan = Column(String)
    id = Column(String)
    root_prio = Column(String)
    root_id = Column(String)
    root_cost = Column(String)
    root_port = Column(String)


class InterfaceQos(Base):
    """"""

    __tablename__ = "InterfaceQos"

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


class DeviceFacts(Base):
    """"""

    __tablename__ = "DeviceFacts"

    unique_id = Column(String(50), primary_key=True)
    serial = Column(String)
    model = Column(String)
    uptime = Column(String)
    software = Column(String)
    username = Column(String)
    password = Column(String)


class UnassignedInterfaces(Base):
    """"""

    __tablename__ = "UnassignedInterfaces"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    interface = Column(String)


class Vrfs(Base):
    """"""

    __tablename__ = "Vrfs"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    vrf = Column(String)


class OspfProcess(Base):
    """"""

    __tablename__ = "OspfProcess"

    unique_id = Column(String(50), primary_key=True)
    id = Column(String)
    process = Column(String)


# Create Tables from above Classes
Base.metadata.create_all(engine)