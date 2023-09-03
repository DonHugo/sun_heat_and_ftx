
```
git add --all
git commit -m "."
git push
git pull
git push
```


collect_sensor_data_mega(3,a,10)

stack = 3
input = a = 1
itirations = 10
collection[i] = collection[0]

age = 36
txt = "My name is John, and I am {}"
print(txt.format(age))

arr = [0,0,0], [1,1,1]



elif msg.topic == "hass/manuell_styrning":
        try:
            x = json.loads(msg.payload.decode())
            if x["state"] == 0:
                solfangare_manuell_styrning = False
            elif x["state"] == 1:
                solfangare_manuell_styrning = True
            logging.debug("solfangare_manuell_styrning: %s", solfangare_manuell_styrning)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)


elif msg.topic == "hass/elpatron":
        try:
            x = json.loads(msg.payload.decode())
            if x["state"] == 0:
                elpatron = "false"
            elif x["state"] == 1:
                elpatron = "true"
            logging.debug("elpatron: %s", elpatron)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)