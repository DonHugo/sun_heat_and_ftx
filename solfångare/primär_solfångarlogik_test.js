

try{
    node.status({fill:"blue",shape:"ring",text:"run"});    
    
        var T1 = flow.get("RTD_1_1"); //Kollektor
        var T2 = flow.get("RTD_1_2"); //Tank_bottom
        var T3 = flow.get("RTD_1_8"); //Tank_top
        var set_temp_tank_1 = 65; // Maximal temperatur i tanken under normal drift. (Inställbar 15 °C till 90 °C med fabriksinställning 65 °C)
        var dTStart_tank_1 = 7; // Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen startar laddnig mot tanken. (Inställbar 3 °C till 40 °C med fabriksinställning 7 °C)
        var dTStop_tank_1 = 3; // Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen stannar. (Inställbar 2 till (Set tank1 -2 °C) med fabriksinställning 3 °C)
        var temp_kok = 150; // 
        var dT_temp_kok = (temp_kok - 10) 
        var kylning_kollektor = 95;  
        var dT_kylning_kollektor = 5;
        var main_state = flow.get("state")||0;
        var sub_state = flow.get("sub_state")||0;
        var mode = flow.get("mode"); //sammanslagning av main_state och sub_state 
        var manuell_styrning = flow.get("solfangare_manuell_styrning"); // TODO: byta till manuell_styrning
        var manuell_pump = flow.get("pump_solfangare");
        var dT_running;
        var dT_running_nice;
        
        var overheated = false;
    
        var dT = T1-T2;
        var dT_nice = parseFloat(dT.toFixed(2));
        var pump = flow.get("pump")||false;
    
        var msg1 = {};
        var msg2 = {};
        var msg3 = {};
        var msg4 = {};
        var msg5 = {};
        
    //===============================================================//
    //==skapar en entitet för att mäta energimängd när pumpen är på==//
        if (pump === true){
          dT_running =  T1-T2;
          dT_running_nice = parseFloat(dT_running.toFixed(2));
        }
        else{
            dT_running =  0;
            dT_running_nice = parseFloat(dT_running.toFixed(2));
        }
    //===============================================================//
    
        if (manuell_styrning == true) {
            state = 1; // Manuell drift
        }
        else if(overheated == true ||  T1 > temp_kok || (pump == false && T1 > kylning_kollektor)){
            state = 2; // överhettning
        }
        else if (condition) {
            state = 3; // impulsdrift
        }
        else if (condition) {
            state = 4; // normaldrift
        }
        else{
            state = 5; //out of bounds
        }
    


    //===============================================================//
        if (T1 >= temp_kok ){
            overheated = true;
            flow.set("mode", "20");
               flow.set("dT_temp_kok", dT_temp_kok);
               flow.set("overheated", overheated);
               node.status({fill:"green",shape:"dot",text:"20"});
        }
        else if(overheated == true && T1 < 140 ){
            overheated = false;
            flow.set("mode", "21")
            flow.set("main_state", 0)
            flow.set("dT_temp_kok", dT_temp_kok)
            flow.set("overheated", overheated);
            node.status({fill:"green",shape:"dot",text:"21"});    
        }
    //===============================================================//
    
    
    //===============================================================//
        if (manuell_styrning === true){
            if (manuell_pump === true){
                pump = true;
                //mode = 06;
                flow.set("mode", "06")
                flow.set("main_state", 0)
                flow.set("sub_state", 6)
                node.status({fill:"green",shape:"dot",text:"06"});
            }
            else{
                pump = false;
                //mode = 07;
                flow.set("mode", "07")
                flow.set("pump", pump);
                flow.set("main_state", 0)
                flow.set("sub_state", 7)
                node.status({fill:"green",shape:"dot",text:"07"});
            }
        }
        else{
               //Om pumpen är av(main_state 0) eller om pumpen är på pga "dra fram vatten impuls"  
            if ((main_state == 0 && overheated === false) || (main_state == 1 && sub_state == 1 && overheated === false)){
                node.status({fill:"green",shape:"ring",text:"1"});
                //starta pumpen om dT är lika med eller större än satt nivå och T2 är under satt nivå
                if(dT >= dTStart_tank_1 && T2 <= set_temp_tank_1 ){
                    pump = true;
                    //mode = 12;
                    flow.set("mode", "12")
                    flow.set("pump", pump);
                    flow.set("main_state", 1)
                    flow.set("sub_state", 2)
                    node.status({fill:"green",shape:"dot",text:"12"});
                }
                //starta pump om kollektor blir för varm men inte om den överstiger "temp_kok" grader
                else if(T1 >= kylning_kollektor){
                    pump = true;
                    //mode = 13;
                    flow.set("mode", "13")
                    flow.set("pump", pump);
                    flow.set("main_state", 1)
                    flow.set("sub_state", 3)
                    node.status({fill:"green",shape:"dot",text:"13"});
                }
                else{
                    node.status({fill:"green",shape:"dot",text:"pump av"});
                }
            }
            //Om pumpen är på men inte om  "dra fram vatten impuls" är igång
            if (main_state == 1 && !(main_state == 1 && sub_state == 1)){
                node.status({fill:"green",shape:"ring",text:"0"});
                //stoppa pumpen när dT går under satt nivå
                if(dT <= dTStop_tank_1 ){
                    pump = false;
                    //mode = 02;
                    flow.set("mode", "02")
                    flow.set("pump", pump);
                    flow.set("main_state", 0)
                    flow.set("sub_state", 2)
                    node.status({fill:"green",shape:"dot",text:"02"});
                }
                //stoppa pumpen när den nåt rätt nivå och kollektor inte är för varm
                else if(T2 >= set_temp_tank_1+2 && T1 <= kylning_kollektor){
                    pump = false;
                    //mode = 03;
                    flow.set("mode", "03")
                    flow.set("pump", pump);
                    flow.set("main_state", 0)
                    flow.set("sub_state", 3)
                    node.status({fill:"green",shape:"dot",text:"03"});
                }
                //stoppa pumpen när kollektor har börjat koka
                else if(T1 >= temp_kok ){
                    pump = false;
                    //mode = 04;
                    overheated = true;
                    flow.set("overheated", overheated);
                    flow.set("mode", "04")
                    flow.set("pump", pump);
                    flow.set("main_state", 0)
                    flow.set("sub_state", 4)
                    node.status({fill:"green",shape:"dot",text:"04"});
                }
                else{
                    node.status({fill:"green",shape:"dot",text:"pump på"});
                }
            } 
        }
    
        
    
        msg1.payload = pump;
    //	msg2.payload = {
    //			"T1": T1,
    //			"T2": T2,
    //			"T3": T3,
    //			"dT": dT_nice,
    //			"dT_running": dT_running_nice,
    //			"Pump": pump,
    //			"set_temp_tank_1": set_temp_tank_1,
    //			"dTStart_tank_1": dTStart_tank_1,
    //			"dTStop_tank_1": dTStop_tank_1,
    //			"main_state": main_state,
    //			"sub_state": sub_state,
    //			"temp_kok": temp_kok,
    //	        "kylning_kollektor": kylning_kollektor,
    //			
    //}
            msg2.payload = {
                "Pump": pump,
                "main_state": main_state,
                "sub_state": sub_state,
                "mode": mode,
                "overheated": overheated,
            };
        msg3.payload = dT_nice;
        msg4.payload = main_state;
        msg5.payload = sub_state;
    
        return [msg1,msg2,msg3,msg4,msg5];
    }
    
    catch(err){
        node.error(err)
        node.status({fill:"red",shape:"ring",text:"error"});
    }
    