from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
import app.Database.DbOperations as DbOps

engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/XEOps_3', echo=True,
                       pool_size=15000)
# Open database connections
Db_conn = sessionmaker(bind=engine)



def query_interfaces(device):
    session = Db_conn()
    interfaces = session.query(DbOps.Interfaces_Main).filter(DbOps.Interfaces_Main.id.like(device))
    session.close()

    return interfaces

def query_bgp_status(device):
    session = Db_conn()
    bgp_status = session.query(DbOps.Bgp_Main).filter(DbOps.Bgp_Main.id.like(device))
    session.close()

    return bgp_status

def query_ospf_status(device):
    session = Db_conn()
    ospf_status = session.query(DbOps.Ospf_Main).filter(DbOps.Ospf_Main.id.like(device))
    session.close()

    return ospf_status

def query_arp_table(device):

    session = Db_conn()
    arp_table = session.query(DbOps.Arp_Main).filter(DbOps.Arp_Main.id.like(device))
    session.close()

    return arp_table

def query_cdp(device):
    session = Db_conn()
    cdp = session.query(DbOps.Cdp_Main).filter(DbOps.Cdp_Main.id.like(device))
    session.close()

    return cdp

def query_trunks(device):
    session = Db_conn()
    trunks = session.query(DbOps.Trunks_Main).filter(DbOps.Trunks_Main.id.like(device))
    session.close()

    return trunks

def query_access_ports(device):
    session = Db_conn()
    access_ports = session.query(DbOps.AccessInterfaces_Main).filter(DbOps.AccessInterfaces_Main.id.like(device))
    session.close()

    return access_ports

def query_port_channels(device):
    session = Db_conn()
    port_channels = session.query(DbOps.PoChannels_Main).filter(DbOps.PoChannels_Main.id.like(device))
    session.close()

    return port_channels

def query_mac_to_arp(device):
    session = Db_conn()
    mac_to_arp = session.query(DbOps.ArpMac_Main).filter(DbOps.ArpMac_Main.id.like(device))
    session.close()

    return mac_to_arp

def query_vlans(device):
    session = Db_conn()
    vlans = session.query(DbOps.Vlans_Main).filter(DbOps.Vlans_Main.id.like(device))
    session.close()

    return vlans

def query_spanning_tree(device):
    session = Db_conn()
    spanning_tree = session.query(DbOps.SpanningTree_Main).filter(DbOps.SpanningTree_Main.id.like(device))
    session.close()

    return spanning_tree

def query_vrfs(device):
    session = Db_conn()
    vrfs = session.query(DbOps.Vrfs_Main).filter(DbOps.Vrfs_Main.id.like(device))
    session.close()
    
    return vrfs

def query_qos(device):
    session = Db_conn()
    qos = session.query(DbOps.InterfaceQos_Main).filter(DbOps.InterfaceQos_Main.id.like(device))
    session.close()
    
    return qos

def query_prefix_list(device):
    session = Db_conn()
    prefix_list = session.query(DbOps.PrefixList_Main).filter(DbOps.PrefixList_Main.id.like(device))
    session.close()

    return prefix_list

def query_route_maps(device):
    session = Db_conn()
    route_map = session.query(DbOps.RouteMaps_Main).filter(DbOps.RouteMaps_Main.id.like(device))
    session.close()

    return route_map

def query_ospf_processes(device):
    session = Db_conn()
    proccess = session.query(DbOps.OspfProcess_Main).filter(DbOps.OspfProcess_Main.id.like(device))
    session.close()

    return proccess

def query_device_inventory():
    session = Db_conn()
    devices = session.query(DbOps.DeviceFacts_Main).all()
    session.close()

    return devices

def query_routes(device):
    session = Db_conn()
    routes = session.query(DbOps.RoutingTable).filter(DbOps.RoutingTable.id.like(device))
    session.close()

    return routes

def query_hsrp(device):
    session = Db_conn()
    hsrp = session.query(DbOps.Hsrp_Main).filter(DbOps.Hsrp_Main.id.like(device))
    session.close()

    return hsrp

def query_ospf_routers(device):
    session = Db_conn()
    hsrp = session.query(DbOps.OspfRouterTable_Main).filter(DbOps.OspfRouterTable_Main.id.like(device))
    session.close()

    return hsrp

def query_dmvpn_status(device):
    session = Db_conn()
    hsrp = session.query(DbOps.DmvpnTable_Main).filter(DbOps.DmvpnTable_Main.id.like(device))
    session.close()

    return hsrp

def query_dmvpn_type(device):
    session = Db_conn()
    hsrp = session.query(DbOps.DmvpnCountTable_Main).filter(DbOps.DmvpnCountTable_Main.id.like(device))
    session.close()

    return hsrp

def query_dmvpn_interfaces(device):
    session = Db_conn()
    hsrp = session.query(DbOps.DmvpnInterfacesTable_Main).filter(DbOps.DmvpnInterfacesTable_Main.id.like(device))
    session.close()

    return hsrp