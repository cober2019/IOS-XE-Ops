
.. image:: https://travis-ci.com/cober2019/IOS-XE-Ops.svg?branch=main
    :target: https://travis-ci.com/cober2019/IOS-XE-Ops
.. image:: https://img.shields.io/badge/NETCONF-required-blue
    :target: -
.. image:: https://img.shields.io/badge/IOS--XE-required-blue
    :target: -
.. image:: https://img.shields.io/badge/Hardware-ISR--4331X%7CView&Configure-green
    :target: - 
.. image:: https://img.shields.io/badge/Hardware-ASR--1001X%7CViewConfig-green
    :target: - 
.. image:: https://img.shields.io/badge/Hardware-CAT--3850%7CViewConfig-green
    :target: -
.. image:: https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg
    :target: https://developer.cisco.com/codeexchange/github/repo/cober2019/IOS-XE-Ops

IOS-XE-Ops
===========

    Docker Link:
        - https://hub.docker.com/r/cober2019/ios_xe_ops
    Docker Commands:
        - docker pull docker pull cober2019/ios_xe_ops:version1.3
        - docker run -p 5000:5000  -d cober2019/ios_xe_ops:version1.3

**Contributions**
------------------

    - If you do use this program PLEASE report any issues to the issues section of my repo.
    - If you want to see any features PLEASE request
    - If you want to contribute and have access to IOS-XE device PLEASE reach out to me via LinkedIn or Email, https://www.linkedin.com/in/chris-oberdalhoff-43292b56/,         cober91130@gmail.com
        
**Known Issues:**
-----------------
 
  + Code Version Fuji Version 16.7.2 (ISR 4331): Device rebooting when applying QoS policy to Gig Interface
  
Usage:
=========

**Logging In:**
----------------

    - When logging in the main page may take some time to load. This usually depends on how many interfaces are on the device. Reason, there is no database
      so all information is collected in real time.
    
    
**Session Logging:**
--------------------

    - All session output is stored in the local program directory, app/logs
    
**Configs:**
---------------

    - All configs whether pass or fail are stored in the local program directory, app/configs as XML files

**View, Add, Modify interfaces:**
---------------------------------

.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/interfaces.PNG

**Modify Interface:**

    When modifying the selected interface field will be preloaded. Leave no desired option in there current state.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/modifyInterface.PNG

**Modifying Management Interface:**
-----------------------------------

    If you select the interface in which you are currently using for your connection you will be warned.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/InterfaceWarning.PNG

**Clearing Interfaces:**
------------------------

    Clear interface statistics with with "Clear Counters" button. Once clicked you will see "Clearing." Once cleared the button will reset.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/ClearingInterface.PNG

**Add Interface:**
-------------------

   You can add a new "logical" interfaces. .i.e tunnel, loopback, vlan etc.
   
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/NewInterface.PNG

**ARP Table:**
---------------
    
    View current ARP entries. You can also clear the table with the "Clear Arp" button. Once clicked, you will see clearing status:
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/ARP.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/ClearArp.PNG

**Routing Tables:**
-------------------

    Currently OSPF and BGP are the only supported routing protocols. You can view and modify neighbors. If no protocols are enabled then you won't see
    any tables. If you want to add a new protocol then use the "Routing" tab in the navbar.

**Add Protocol:**
------------------

.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/SelectRouintg.PNG
    
**BGP:**
---------------
    
    Refresh the BGP neighbor table or add/modify neighbors. If you select modify neighbor the form will be loaded with the current AS and select neighbor. Adding a neighbor is       the same except the neighbor field will be blank.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/BGPTable.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/BGPNeighborModify.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/AddBGPNeighbor.PNG


**OSPF:**
---------------
    
    Refresh OSPF neighbor table or add/modify neighbors. If you see a table with no neighbors, this indicates OSPF is enabled with no estblished neighbors.
    When Adding neighbors/networks, OSPF Proccesses are preloaded in the form.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/OSPFTables.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/OSPFProcess.PNG

**Routing Tables:**
--------------------

    View the device's current routing table by clicking the "Get Routes". Once the routes are fetched, you can search with the search box and refresh routes.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/GetRoutes.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/ViewRouting.PNG


**QOS**
---------

    View and modify current QOS interface policies. If an interface has a policy you will see '(Qos)' in blue next to the interface. You can also see the current
    queue statistics below the interfaces table. If you want to modify an interface QoS, service policies will be preload into your form. Policies are available
    via dropdown menu. This program does not modify the queues, only interface application.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/QOS.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/QOSOutput.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/QoSfORM.PNG
