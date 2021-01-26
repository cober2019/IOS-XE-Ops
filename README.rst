
.. image:: https://travis-ci.com/cober2019/IOS-XE-Ops.svg?branch=main
    :target: https://travis-ci.com/cober2019/IOS-XE-Ops
.. image:: https://img.shields.io/badge/NETCONF-required-blue
    :target: -
.. image:: https://img.shields.io/badge/IOS--XE-required-blue
    :target: -
.. image:: https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg
    :target: https://developer.cisco.com/codeexchange/github/repo/cober2019/IOS-XE-Ops

IOS-XE-Ops
===========

    **IOS-XE-Ops is designed to give you a summary view of your device. These features include:**
    
        - Interfaces details both from a cli view and a custom flask view
        - Full routing tables plus a cli view from the table and database perspective
        - Interfaces qos plus a cli view of you current queueing stats
        - Arp table
        - Routing neighbors (BGP & OSPF)
        - Configure/Modify interfaces
        - Apply service policies
        - Clear ARP table
        - Refresh Tables
    
        
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

