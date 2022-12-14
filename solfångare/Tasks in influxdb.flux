option task = {name: "Notebook Task for DS-avluft-day-max", every: 24h}
option v = {timeRangeStart: 2021-01-01T00:00:00Z, timeRangeStop: 2022-05-31T17:22:56Z}

from(bucket: "hass")
    |> range(start: v.timeRangeStart)
    |> filter(
        fn: (r) =>
            r["entity_id"] == "effekt_varmevaxlare" or r["entity_id"] == "avluft" or r["entity_id"] == "4_avluft",
    )
    |> filter(fn: (r) => r["_field"] == "value")
    |> filter(fn: (r) => r["_measurement"] == "°C")
    |> aggregateWindow(every: 1d, fn: max)
    |> set(key: "aggregate", value: "max")
    |> to(bucket: "hass-ds-daily")