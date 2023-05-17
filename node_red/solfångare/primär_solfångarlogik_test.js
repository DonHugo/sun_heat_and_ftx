try {
    node.status({ fill: "blue", shape: "ring", text: "run" });
    //=============Input values=============//
//    var T1 = flow.get("RTD_1_1") || 0; //Kollektor
//    var T2 = flow.get("RTD_1_2") || 0; //Tank_bottom
//    var T3 = flow.get("RTD_1_8") || 0; //Tank_top
    var T1 = global.get("RTD_1_1") || 0; //Kollektor
    var T2 = global.get("RTD_1_2") || 0; //Tank_bottom
    var T3 = global.get("RTD_1_8") || 0; //Tank_top
    var manuell_styrning = flow.get("solfangare_manuell_styrning") || false;
    var manuell_pump = flow.get("pump_solfangare") || false;
    //=============set variables=============//
    var set_temp_tank_1 = flow.get("set_temp_tank_1") || 0; // Maximal temperatur i tanken under normal drift. (Inställbar 15 °C till 90 °C med fabriksinställning 65 °C)
    var dTStart_tank_1 = flow.get("dTStart_tank_1") || 0; // Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen startar laddnig mot tanken. (Inställbar 3 °C till 40 °C med fabriksinställning 7 °C)
    var dTStop_tank_1 = flow.get("dTStop_tank_1") || 0; // Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen stannar. (Inställbar 2 till (Set tank1 -2 °C) med fabriksinställning 3 °C)
    var kylning_kollektor = flow.get("kylning_kollektor") || 0;
    var temp_kok = flow.get("temp_kok") || 0; //
    var normal_drift_nedkylning = flow.get("normal_drift_nedkylning") || false;
    //=============process variables=============//
    var dT_temp_kok = 10;
    var reset_temp_kok = temp_kok - dT_temp_kok;
    var dT_kylning_kollektor = 5;
    var reset_kylning_kollektor = kylning_kollektor - dT_kylning_kollektor;
    var dT_set_temp_tank_1 = 5;
    var reset_set_temp_tank_1 = set_temp_tank_1 - dT_set_temp_tank_1;
    var dT_running;
    var dT = T1 - T2;
    var sun = flow.get("sun") || 0;
    //var impuls_delay_pump_off =10000 //300000; // 5min
    //var impuls_delay_pump_on = 5000 //60000; // 1min
    //var impuls_delay_pump_timer = 0;
    //var impuls_delay_pump_state = flow.get("impuls_delay_pump_state") || "impuls_delay_pump_off";
    //=============Output values=============//
    var main_state = flow.get("main_state") || 0;
    var sub_state = flow.get("sub_state") || 0;
    var mode = flow.get("mode") || 0; //sammanslagning av main_state och sub_state     
    var mode_string;
    var dT_running_nice;
    var overheated = flow.get("overheated") || false;
    var cooling_kollektor = flow.get("cooling_kollektor") || false;
    var dT_nice = parseFloat(dT.toFixed(2));
    var pump = flow.get("pump") || false;
    //=============msg syntax=============//
    var msg1 = {};
    var msg2 = {};
    var msg3 = {};

    //===============================================================//
    //==skapar en entitet för att mäta energimängd när pumpen är på==//
    if (pump === true) {
        dT_running = T1 - T2;
        dT_running_nice = parseFloat(dT_running.toFixed(2));
    }
    else {
        dT_running = 0;
        dT_running_nice = parseFloat(dT_running.toFixed(2));
    }
    //===============================================================//

    if (manuell_styrning === true) {
        main_state = 1; // Manuell drift
        flow.set("main_state", main_state);
        node.status({ fill: "blue", shape: "ring", text: "run - main_state 1" });
    }
    else if (overheated === true || T1 >= temp_kok) {
        main_state = 2; // avstängning pga överhettning i kollektor
        flow.set("main_state", main_state);
        node.status({ fill: "blue", shape: "ring", text: "run - main_state 2" });
    }
    else if ((pump === false && T1 >= kylning_kollektor) || cooling_kollektor === true) {
        main_state = 5; // nedkylning av kollektor
        flow.set("main_state", main_state);
        node.status({ fill: "blue", shape: "ring", text: "run - main_state 5" });
    }
    else if ((dT >= dTStart_tank_1 || normal_drift_nedkylning === true) || (pump === true )){
        main_state = 4; // normaldrift
        flow.set("main_state", main_state);
        node.status({ fill: "blue", shape: "ring", text: "run - main_state 4" });
    }
    else {
        main_state = 4; // normaldrift
        flow.set("main_state", main_state);
        node.status({ fill: "blue", shape: "ring", text: "run - main_state 4" });
    }

    switch (main_state) {
        case 1: // Manuell drift
            if (manuell_pump === true) {
                pump = true;
                flow.set("pump", pump)
                flow.set("mode", "11")
                //flow.set(mode_string, '\'Manuell_drift_pump_påslagen\'');
                flow.set("sub_state", 1)
                node.status({ fill: "green", shape: "dot", text: "11 - Manuell drift pump påslagen" });
            }
            else {
                pump = false;
                flow.set("pump", pump);
                flow.set("mode", "12");
                //flow.set(mode_string, "Manuell_drift_pump_avslagen");
                flow.set("sub_state", 2);
                node.status({ fill: "green", shape: "dot", text: "12 - Manuell drift pump avslagen" });
            }
            flow.set("main_state", main_state);
            msg1.payload = pump;
            msg2.payload = {
                "Pump": pump,
                "main_state": main_state,
                "sub_state": sub_state,
                "mode": mode,
                //"mode_string": mode_string,
                "overheated": overheated,
                "cooling_kollektor": cooling_kollektor,
                //               "impuls_delay_pump_state": impuls_delay_pump_state,
                "T1": T1,
                "T2": T2,
            };
            msg3.reset = true;
            return [msg1, msg2, msg3];

        case 2: // avstängning pga överhettning i kollektor

            if (T1 >= temp_kok && overheated === false) {
                pump = false;
                overheated = true;
                flow.set("overheated", overheated);
                flow.set("pump", pump);
                flow.set("mode", "21");
                //flow.set(mode_string, '\'Pump avslagen pga för hög temperatur i kollektor\'');
                flow.set("sub_state", 1);
                node.status({ fill: "green", shape: "dot", text: "21 - Pump avslagen pga för hög temperatur i kollektor" });
            }
            else if (overheated === true && T1 < reset_temp_kok) {
                overheated = false;
                flow.set("overheated", overheated);
                flow.set("mode", "22");
                //flow.set(mode_string, '\'Temperatur i kollektor är under risknivå\'');
                flow.set("sub_state", 2);
                node.status({ fill: "green", shape: "dot", text: "22 - Temperatur i kollektor är under risknivå" });
            }
            else {
                flow.set("mode", "23");
                //flow.set(mode_string, '\'Out of Bounds\'');
                flow.set("sub_state", 3);
                node.status({ fill: "red", shape: "dot", text: "23 - Pump avslagen pga för hög temperatur i kollektor" });
            }
            flow.set("main_state", main_state);
            msg1.payload = pump;
            msg2.payload = {
                "Pump": pump,
                "main_state": main_state,
                "sub_state": sub_state,
                "mode": mode,
                //"mode_string": mode_string,
                "overheated": overheated,
                "cooling_kollektor": cooling_kollektor,
                //               "impuls_delay_pump_state": impuls_delay_pump_state,
                "T1": T1,
                "T2": T2,
            };
            msg3.reset = true;
            return [msg1, msg2, msg3];

        case 4: // normaldrift
            if ((T2 < set_temp_tank_1 && normal_drift_nedkylning === false && dT >= dTStart_tank_1 && pump === false) || (T2 < set_temp_tank_1 && normal_drift_nedkylning === false && pump === true && dT > dTStop_tank_1)) {
                pump = true;
                flow.set("pump", pump);
                flow.set("mode", "41");
                //flow.set(mode_string, "Normaldrift - Pump påslagen");
                flow.set("sub_state", 1);
                node.status({ fill: "green", shape: "dot", text: "41 - Normaldrift - Pump påslagen" });
            }
            else if (dT <= dTStop_tank_1) {
                pump = false;
                //normal_drift_nedkylning = true;
                //flow.set("normal_drift_nedkylning", normal_drift_nedkylning)
                flow.set("pump", pump);
                flow.set("mode", "42");
                //flow.set(mode_string, "Normaldrift - Pump avslagen, fördröjning");
                flow.set("sub_state", 2);
                node.status({ fill: "green", shape: "dot", text: "42 - Normaldrift - Pump avslagen, dT under gränsvärdet" });
            }
            else if (T2 >= set_temp_tank_1) {
                pump = false;
                normal_drift_nedkylning = true;
                flow.set("normal_drift_nedkylning", normal_drift_nedkylning)
                flow.set("pump", pump);
                flow.set("mode", "43");
                //flow.set(mode_string, "Normaldrift - Pump avslagen, fördröjning");
                flow.set("sub_state", 3);
                node.status({ fill: "green", shape: "dot", text: "43 - Normaldrift - Pump avslagen, T2 över gränsvärdet" });
            }

            else if (T2 < reset_set_temp_tank_1 && normal_drift_nedkylning === true) {
                normal_drift_nedkylning = false;
                flow.set("normal_drift_nedkylning", normal_drift_nedkylning)
                flow.set("mode", "44");
                //flow.set(mode_string, '\'Normaldrift - Pump avslagen\'');
                flow.set("sub_state", 4);
                node.status({ fill: "green", shape: "dot", text: "44 - Normaldrift - Pump avslagen" });
            }

            flow.set("main_state", main_state);
            msg1.payload = pump;
            msg2.payload = {
                "Pump": pump,
                "main_state": main_state,
                "sub_state": sub_state,
                "mode": mode,
                //"mode_string": mode_string,
                "overheated": overheated,
                "cooling_kollektor": cooling_kollektor,
                "normal_drift_nedkylning": normal_drift_nedkylning,
                //               "impuls_delay_pump_state": impuls_delay_pump_state,
                "T1": T1,
                "T2": T2,
            };
            msg3.reset = true;
            return [msg1, msg2, msg3];

        case 5: //nedkylning av kollektor
            if (cooling_kollektor === true && T1 < reset_kylning_kollektor) {
                pump = false;
                cooling_kollektor = false;
                flow.set("cooling_kollektor", cooling_kollektor);
                flow.set("pump", pump);
                flow.set("mode", "52");
                //flow.set(mode_string, "Pump avsalgen, kylning av kollektor är klar");
                flow.set("sub_state", 2);
                node.status({ fill: "green", shape: "dot", text: "52 - Pump avsalgen, kylning av kollektor är klar" });
            }
            else {
                pump = true;
                cooling_kollektor = true;
                flow.set("cooling_kollektor", cooling_kollektor);
                flow.set("pump", pump);
                flow.set("mode", "51");
                //flow.set(mode_string, "Pump påslagen och kylning av kollektor pågår");
                flow.set("sub_state", 1);
                node.status({ fill: "green", shape: "dot", text: "51 - Pump påslagen och kylning av kollektor pågår" });
            }

            flow.set("main_state", main_state);
            msg1.payload = pump;
            msg2.payload = {
                "Pump": pump,
                "main_state": main_state,
                "sub_state": sub_state,
                "mode": mode,
                //"mode_string": mode_string,
                "overheated": overheated,
                "cooling_kollektor": cooling_kollektor,
                "normal_drift_nedkylning": normal_drift_nedkylning,
                //                "impuls_delay_pump_state": impuls_delay_pump_state,
                "T1": T1,
                "T2": T2,
            };
            msg3.reset = true;
            return [msg1, msg2, msg3];
    }
}

catch (err) {
    node.error(err)
    node.status({ fill: "red", shape: "ring", text: "error" });
}