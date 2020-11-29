
.. image:: https://travis-ci.com/cober2019/IOS-XE-Ops.svg?branch=main
    :target: https://travis-ci.com/cober2019/IOS-XE-Ops
.. image:: https://img.shields.io/badge/NETCONF-required-blue
    :target: -
.. image:: https://img.shields.io/badge/IOS--XE-required-blue
    :target: -

    
IOS-XE-Ops (Beta) 
======

    Docker Link:
        - https://hub.docker.com/r/cober2019/ios_xe_ops: 
    Docker Commands:
        - docker pull cober2019/ios_xe_ops:ops_01
        - docker run -p 5000:5000  -d cober2019/ios_xe_ops:ops_01
    
Known Issues:
----------
 
  + Code Version Fuji Version 16.7.2 (ISR 4331): Device rebooting when applying QoS policy to Gig Interface
  
Features:
-----------

**View, Add, Modify interfaces:**

.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/interfaces.PNG

**Modify Interface:**

    When modifying the interface field will be preloaded. Modification options show below. If you don't want to change a setting, dont modify the input box

.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/modifyInterface.PNG

**Modifying Management Interface:**

    If you select the interface in which you are currently using for your connection you will be warned.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/InterfaceWarning.PNG

**Clearing Interfaces:**

    You can also clear interface statistics with with "Clear Counters" button. Once clicked you will see "Clearing." Once cleared the button will reset.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/ClearingInterface.PNG

**Add Interface:**

   You can add a new "logical" interface. .i.e tunnel, loopback, vlan etc.
   
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/NewInterface.PNG

**ARP Table:**
    
    View current ARP entries. You can also clear the table with the "Clear Arp" button. Once clicked, you will see clearing status:
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/ARP.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/ClearArp.PNG


