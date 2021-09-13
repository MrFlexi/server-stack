sap.ui.define([
	"sap/ui/core/mvc/Controller",
	'sap/ui/model/json/JSONModel'
  ], function(Controller,JSONModel) {
	"use strict";

	//var socket = io.connect('ws://' + document.domain + ':' + location.port + '', { transports: ['websocket'] });
	var socket = io();

	var oModelMenu = new sap.ui.model.json.JSONModel();
	var oModelDevices = new sap.ui.model.json.JSONModel();
  
	var CController = Controller.extend("view.App", {
  
	  onInit: function() {	

		oModelMenu.loadData("/static/menu.json");
		this.getView().setModel(oModelMenu);


		// oModelDevices.loadData("http://api.szaroletta.de/device_list");
		this.getView().setModel(oModelDevices,"oModelDevices");	
		
		
		socket.on('connect', function () {
			console.log(socket.id);
		    socket.emit('connected', {data: 'I\'m connected!'});
		});

		socket.on('Devices', function (msg) {
			var in_json = jQuery.parseJSON(msg.DeviceList);
				oModelDevices.setData(in_json);
		   
		});


	  },
	  
	  onBeforeRendering: function() {
	
	  },
	  
	  onAfterRendering: function() {
	
	  },
	  
	  onExit: function() {
  
			console.log("onExit() of controller called...");
			alert("onExit function called");
		},
	  
	  onPress: function(Event) {
		this.getView().destroy();
	  },

	  onSliderliveChange: function (oEvent) {
		socket.emit('main_controller_value_changed', { data: oModelMainController.getData() });
	},

	  onItemSelect: function (oEvent) {
		var item = oEvent.getParameter('item');
		var viewId = this.getView().getId();
		sap.ui.getCore().byId(viewId + "--pageContainer").to(viewId + "--" + item.getKey());
	}
  
	});

	return CController;
  });