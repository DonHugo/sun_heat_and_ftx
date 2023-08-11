collect_sensor_data_mega(3,a,10)

stack = 3
input = a = 1
itirations = 10
collection[i] = collection[0]

age = 36
txt = "My name is John, and I am {}"
print(txt.format(age))

arr = [0,0,0], [1,1,1]

if (solfangare_manuell_styrning === true){
        if (pump_solfangare === true){
            pump = true;
            //mode = 06;
            flow.set("mode", "06")
            flow.set("state", 0)
		    flow.set("sub_state", 6)
		    node.status({fill:"green",shape:"dot",text:"06"});
        }
        else{
            pump = false;
            //mode = 07;
            flow.set("mode", "07")
		    flow.set("pump", pump);
		    flow.set("state", 0)
		    flow.set("sub_state", 7)
		    node.status({fill:"green",shape:"dot",text:"07"});
        }
    }
else{
       	//Om pumpen är av(state 0) eller om pumpen är på pga "dra fram vatten impuls"  
    	if ((state == 0 && overheated === false) || (state == 1 && sub_state == 1 && overheated === false)){
    		node.status({fill:"green",shape:"ring",text:"1"});
    		//starta pumpen om dT är lika med eller större än satt nivå och T2 är under satt nivå
    		if(dT >= dTStart_tank_1 && T2 <= set_temp_tank_1 ){
    			pump = true;
    			//mode = 12;
    			flow.set("mode", "12")
    			flow.set("pump", pump);
    			flow.set("state", 1)
    			flow.set("sub_state", 2)
    			node.status({fill:"green",shape:"dot",text:"12"});
    		}
    		//starta pump om kollektor blir för varm men inte om den överstiger "temp_kok" grader
    		else if(T1 >= kylning_kollektor){
    			pump = true;
    			//mode = 13;
    			flow.set("mode", "13")
    			flow.set("pump", pump);
    			flow.set("state", 1)
    			flow.set("sub_state", 3)
    			node.status({fill:"green",shape:"dot",text:"13"});
    		}
    		else{
    		    node.status({fill:"green",shape:"dot",text:"pump av"});
    		}
    	}
    	//Om pumpen är på men inte om  "dra fram vatten impuls" är igång
    	if (state == 1 && !(state == 1 && sub_state == 1)){
    		node.status({fill:"green",shape:"ring",text:"0"});
    		//stoppa pumpen när dT går under satt nivå
    		if(dT <= dTStop_tank_1 ){
    			pump = false;
    			//mode = 02;
    			flow.set("mode", "02")
    			flow.set("pump", pump);
    			flow.set("state", 0)
    			flow.set("sub_state", 2)
    			node.status({fill:"green",shape:"dot",text:"02"});
    		}
    		//stoppa pumpen när den nåt rätt nivå och kollektor inte är för varm
    		else if(T2 >= set_temp_tank_1+2 && T1 <= kylning_kollektor){
    			pump = false;
    			//mode = 03;
    			flow.set("mode", "03")
    			flow.set("pump", pump);
    			flow.set("state", 0)
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
    			flow.set("state", 0)
    			flow.set("sub_state", 4)
    			node.status({fill:"green",shape:"dot",text:"04"});
    		}
    		else{
    		    node.status({fill:"green",shape:"dot",text:"pump på"});
    		}
    	} 
