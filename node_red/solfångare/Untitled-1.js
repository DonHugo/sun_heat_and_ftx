
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
                flow.set("mode", "11")
                //flow.set(mode_string, '\'Manuell_drift_pump_påslagen\'');

                flow.set("mode", "12");
                //flow.set(mode_string, "Manuell_drift_pump_avslagen");
 

        case 2: // avstängning pga överhettning i kollektor


                flow.set("mode", "21");
                //flow.set(mode_string, '\'Pump avslagen pga för hög temperatur i kollektor\'');

                flow.set("mode", "22");
                //flow.set(mode_string, '\'Temperatur i kollektor är under risknivå\'');

                flow.set("mode", "23");
                //flow.set(mode_string, '\'Out of Bounds\'');
 

        case 4: // normaldrift

                flow.set("mode", "41");
                //flow.set(mode_string, "Normaldrift - Pump påslagen");

                flow.set("mode", "42");
                //flow.set(mode_string, "Normaldrift - Pump avslagen, fördröjning");

                flow.set("mode", "43");
                //flow.set(mode_string, "Normaldrift - Pump avslagen, fördröjning");

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