try{
    node.status({fill:"blue",shape:"ring",text:"run"});    
        var state = flow.get("state")||0;
        var sub_state = flow.get("sub_state")||0;
        var sun = flow.get("sun");
        var pump = flow.get("pump")||false;
        var T1 = flow.get("RTD_1_1"); //Kollektor
        var T2 = flow.get("RTD_1_2"); //Tank_top
        var T3 = flow.get("RTD_1_8"); //Tank_bottom
        var solfangare_manuell_styrning = flow.get("solfangare_manuell_styrning");
        var dTStop_tank_1 = flow.get("dTStop_tank_1"); // Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen stannar. (Inställbar 2 till (Set tank1 -2 °C) med fabriksinställning 3 °C)
        var temp_kok = flow.get("temp_kok");
        var overheated = flow.get("overheated")||false;
        var msg1 = {};
        var msg2 = {};
        var msg3 = {};
        var msg4 = {};
        var msg5 = {};
        var dT = T1-T2;
        var dT_nice = parseFloat(dT.toFixed(2));
        var mode = flow.get("mode");
    
    
        if (sun == "above_horizon" && solfangare_manuell_styrning === false && dT > 3  && overheated === false){
            switch (state) {
            case  0:
                  pump = true;
                  //mode = 11;
                  flow.set("mode", "11")
                  flow.set("pump", pump);
                  flow.set("state", 1)
                  flow.set("sub_state", 1)
                  node.status({fill:"green",shape:"dot",text:"11"});
               break;
             case 1:
               if(sub_state == 1 ){
                   pump = false;
                   //mode = 01;
                   flow.set("mode", "01")
                   flow.set("pump", pump);
                   flow.set("state", 0)
                   flow.set("sub_state", 1)
                   node.status({fill:"green",shape:"dot",text:"01"});
               }
               node.status({fill:"green",shape:"dot",text:"no action"});
               break;
            }
    
            msg1.payload = pump;
            msg2.payload = {
                "Pump": pump,
                "state": state,
                "sub_state": sub_state,
                "mode": mode,
                };
            msg3.payload = state;
            msg4.payload = sub_state;
    
            return [msg1,msg2,msg3,msg4];
        }
    }
    
    catch(err){
        node.error(err)
        node.status({fill:"red",shape:"ring",text:"error"});
    }
    
    