
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
    Devnet Sandox:
        - Custom ports have been added to login for Cisco Devnet Sandbox usage

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



**Routing Tables:**
-------------------

    Currently OSPF and BGP are the only supported routing protocols. You can view and modify neighbors. If no protocols are enabled then you won't see
    any tables. If you want to add a new protocol then use the "Routing" tab in the navbar.

**Add Protocol:**
------------------

.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/SelectRouintg.PNG


**Routing Tables:**
--------------------

    View the device's current routing table by clicking the "Get Routes". Once the routes are fetched, you can search with the search box and refresh routes.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/iosxeroutetable.PNG


**QOS**
---------

    View and modify current QOS interface policies. If an interface has a policy you will see '(Qos)' in blue next to the interface. You can also see the current
    queue statistics below the interfaces table. If you want to modify an interface QoS, service policies will be preload into your form. Policies are available
    via dropdown menu. This program does not modify the queues, only interface application.
    
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/QOS.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/QOSOutput.PNG
.. image:: https://github.com/cober2019/IOS-XE-Ops/blob/main/images/QoSfORM.PNG
