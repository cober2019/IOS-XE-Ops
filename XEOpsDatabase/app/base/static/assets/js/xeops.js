
$(document).ready(function() {
$('.table').DataTable( {
    "pagingType": "full_numbers"
} );
} );

function clearArp(val){
document.getElementById('clearArp').value  = 'Clearing...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('clearArp').value  = 'Clear Arp';
      $("#arpTable").DataTable().destroy()
      $('#arpTable').html(response.data);
      $('#arpTable').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshArp(val){
document.getElementById('refreshArp').value  = 'Refreshing...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('refreshArp').value  = 'Refresh Arp';
      $("#arpTable").DataTable().destroy()
      $('#arpTable').html(response.data);
      $('#arpTable').DataTable({"pagingType": "full_numbers"});
  },
 });
}


function refreshBgp(val){
document.getElementById('bgpRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('bgpRefresh').value  = 'Poll';
      $("#bgpNeighbors").DataTable().destroy()
      $('#bgpNeighbors').html(response.data);
      $('#bgpNeighbors').DataTable({"pagingType": "full_numbers"});
  },
 });
}


function refreshOspf(val){
document.getElementById('ospfRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('ospfRefresh').value  = 'Poll';
      $("#ospfTable").DataTable().destroy()
      $('#ospfTable').html(response.data);
      $('#ospfTable').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshBgpOnly(val){
document.getElementById('bgpRefreshOnly').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('bgpRefresh').value  = 'Poll';
      $("#bgpNeighborsOnly").DataTable().destroy()
      $('#bgpNeighborsOnly').html(response.data);
      $('#bgpNeighborsOnly').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshOspfOnly(val){
document.getElementById('ospfRefreshOnly').value  = 'Poll...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('ospfRefreshOnly').value  = 'Polling';
      $("#ospfTableOnly").DataTable().destroy()
      $('#ospfTableOnly').html(response.data);
      $('#ospfTableOnly').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function addNeighbor(){
 $.ajax({
  url: '/add_bgp_neighbor',
 });
}

function refreshInterfaces(val){
document.getElementById('interfaceRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('interfaceRefresh').value  = 'Poll';
      $("#interfaceTable").DataTable().destroy()
      $('#interfaceTable').html(response.data);
      $('#interfaceTable').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function moreIntDetails(val){
 document.getElementById(val).value  = 'Getting Details...';
 $.ajax({
  url: '/int_details',
  type: 'POST',
  data: {'details': val},
  success: function(response) {
  document.getElementById(val).value  = 'Interface Details';
      var wind_one = window.open("", "popupWindow", "width=700,height=800,scrollbars=yes");
        wind_one.document.write(response);
  },
 });
}

function cdpDetails(val){
 document.getElementById(val).value  = 'Getting Details...';
 $.ajax({
  url: '/cdp_details',
  type: 'POST',
  data: {'details': val},
  success: function(response) {
    document.getElementById(val).value  = 'CDP Details Details';
      var wind_one = window.open("", "popupWindow", "width=700,height=800,scrollbars=yes");
        wind_one.document.write(response);
  },
 });
}

function spanDetails(val){
 document.getElementById(val).value  = 'Getting Details...';
 $.ajax({
  url: '/span_details',
  type: 'POST',
  data: {'details': val},
  success: function(response) {
    document.getElementById(val).value  = 'Span Details';
      var wind_one = window.open("", "popupWindow", "width=700,height=800,scrollbars=yes");
        wind_one.document.write(response);
  },
 });
}

function hsrpDetails(val){
 document.getElementById(val).value  = 'Getting Details...';
 $.ajax({
  url: '/hsrp_details',
  type: 'POST',
  data: {'details': val},
  success: function(response) {
    document.getElementById(val).value  = 'HSRP Details';
      var wind_one = window.open("", "popupWindow", "width=700,height=800,scrollbars=yes");
        wind_one.document.write(response);
  },
 });
}

function refreshTrunks(val){
document.getElementById('trunkRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('trunkRefresh').value  = 'Poll';
      $("#trunks").DataTable().destroy()
      $('#trunks').html(response.data);
      $('#trunks').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshHsrp(val){
document.getElementById('hsrpRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('hsrpRefresh').value  = 'Poll';
      $("#hsrpTable").DataTable().destroy()
      $('#hsrpTable').html(response.data);
      $('#hsrpTable').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshPortChannels(val){
document.getElementById('portChannelRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('portChannelRefresh').value  = 'Poll';
      $("#portChannels").DataTable().destroy()
      $('#portChannels').html(response.data);
      $('#portChannels').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshVlans(val){
document.getElementById('vlanRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('vlanRefresh').value  = 'Poll';
      $("#vlanTable").DataTable().destroy()
      $('#vlanTable').html(response.data);
      $('#vlanTable').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshCdp(val){
    document.getElementById('cdpRefresh').value  = 'Polling...';
     $.ajax({
      url: '/index',
      type: 'POST',
      data: {'action': val},
      success: function(response) {
      document.getElementById('cdpRefresh').value  = 'Poll';
          $("#cdpTable").DataTable().destroy()
          $('#cdpTable').html(response.data);
          $('#cdpTable').DataTable({"pagingType": "full_numbers"});
      },
     });
}

function refreshAccess(val){
document.getElementById('accessRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('accessRefresh').value  = 'Poll';
      $("#accessTable").DataTable().destroy()
      $('#accessTable').html(response.data);
      $('#accessTable').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshSpan(val){
document.getElementById('rootRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('rootRefresh').value  = 'Poll';
      $("#spanTable").DataTable().destroy()
      $('#spanTable').html(response.data);
      $('#spanTable').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshDmvpnPeer(val){
document.getElementById('peerRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('peerRefresh').value  = 'Poll';
      $("#dmvpnPeers").DataTable().destroy()
      $('#dmvpnPeers').html(response.data);
      $('#dmvpnPeers').DataTable({"pagingType": "full_numbers"});
  },
 });
}

function refreshBorderRouters(val){
document.getElementById('borderRefresh').value  = 'Polling...';
 $.ajax({
  url: '/index',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById('borderRefresh').value  = 'Poll';
      $("#borderrouterRefresh").DataTable().destroy()
      $('#borderrouterRefresh').html(response.data);
      $('#borderrouterRefresh').DataTable({"pagingType": "full_numbers"});
  },
 });
}


$(document).ready(function(){
    $("#myInput").on("keyup", function() {
      var value = $(this).val().toLowerCase();
      $("#myTable tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
      });
    });
});

function moreQosDetails(val){
 $.ajax({
  url: '/qos_details',
  type: 'POST',
  data: {'details': val},
  success: function(response) {
      var wind_three = window.open("", "popupWindow", "width=700,height=800,scrollbars=yes");
        wind_three.document.write(response);
  },
 });
}

function advRouterDetail(val){
 $.ajax({
  url: '/qos_details',
  type: 'POST',
  data: {'details': val},
  success: function(response) {
      var wind_three = window.open("", "popupWindow", "width=700,height=800,scrollbars=yes");
        wind_three.document.write(response);
  },
 });
}

$(document).ready(function(){
    $('#pingForm').submit(function(){
    document.getElementById('ping').value  = 'Pinging...';
     $.ajax({
      url: '/ping/' + val,
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('ping').value  = 'Ping';
       $('#response').html(response.data);
      },
     });
     return false;
    });
});

$(document).ready(function(){
    $('#protocolForm').submit(function(){
     $.ajax({
      url: '/add_new_protocol',
      type: 'POST',
      data: $('form').serialize(),
     });
    });
});


$(document).ready(function(){
    $('#interfaceForm').submit(function(){
     $.ajax({
      url: '/new_int_form',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
       $('#response').html(response.data);
      },
     });
     return false;
    });
});


$(document).ready(function(){
    $('#interfaceForm').submit(function(){
    document.getElementById('modifyInt').value  = 'Submitting...';
     $.ajax({
      url: '/new_int_form',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('modifyInt').value  = 'Submit';
       $('#response').html(response.data);
      },
     });
     return false;
    });
});


$(document).ready(function(){
    $('#qosForm').submit(function(){
    document.getElementById('applyPolicy').value  = 'Applying Policy...';
     $.ajax({
      url: '/modify_qos',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('applyPolicy').value  = 'Apply Policy';
       $('#response').html(response.data);
      },
     });
     return false;
    });
});


$(document).ready(function(){
    $('#interfaceForm').submit(function(){
    document.getElementById('modifyInt').value  = 'Submitting...';
     $.ajax({
      url: '/modify_inteface',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('modifyInt').value  = 'Submit';
       $('#response').html(response.data);
      },
     });
    });
});


$(document).ready(function(){
    $('#accessInterfaceForm').submit(function(){
    document.getElementById('modifyInt').value  = 'Submitting...';
     $.ajax({
      url: '/modify_access_int',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('modifyInt').value  = 'Submit';
       $('#response').html(response.data);
      },
     });
    });
});

function discoverMac(val){
document.getElementById(val).value  = 'Sticking MAC...';
 $.ajax({
  url: '/mac_learning',
  type: 'POST',
  data: {'action': val},
  success: function(response) {
  document.getElementById(val).value  = 'Stick MAC';
      $("#arpMac").DataTable().destroy()
      $('#arpMac').html(response.data);
      $('#arpMac').DataTable({"pagingType": "full_numbers"});
  },
 });
}


function getRouteDetail(val){
   $.ajax({
    url: '/route_details',
    type: 'POST',
    data: {'details': val},
    success: function(response) {
        var wind_two = window.open("", "popupWindow", "width=700,height=800,scrollbars=yes");
          wind_two.document.write(response);
    },
   });
  }



$(document).ready(function(){
    $('#vlanForm').submit(function(){
     $.ajax({
      url: '/add_vlan',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
       $('#response').html(response.data);
      },
     });
     return false;
    });
});


$(document).ready(function(){
    $('#ospfForm').submit(function(){
    document.getElementById('buildAdj').value  = 'Building Adjacency...';
     $.ajax({
      url: '/add_routing_neighbor',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('buildAdj').value  = 'Build Adjacency';
       $('#response').html(response.data);
      },
     });
    });
});

$(document).ready(function(){
    $('#ospfFormCustom').submit(function(){
    document.getElementById('buildAdjCustom').value  = 'Building Adjacency...';
     $.ajax({
      url: '/add_routing_neighbor',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('buildAdjCustom').value  = 'Build Adjacency';
       $('#response').html(response.data);
      },
     });
    });
});


$(document).ready(function(){
    $('#bgpForm').submit(function(){
    document.getElementById('buildAdj').value  = 'Building Adjacency...';
     $.ajax({
      url: '/add_routing_neighbor',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('buildAdj').value  = 'Build Adjacency';
       $('#response').html(response.data);
      },
     });
    });
});

$(document).ready(function(){
    $('#bgpFormCustom').submit(function(){
    document.getElementById('buildAdjCustom').value  = 'Building Adjacency...';
     $.ajax({
      url: '/add_routing_neighbor',
      type: 'POST',
      data: $('form').serialize(),
      success: function(response){
      document.getElementById('buildAdjCustom').value  = 'Build Adjacency';
       $('#response').html(response.data);
      },
     });
    });
});


















