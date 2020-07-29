# victron_mec_meter
Use Mec meter as grid meter for victron device. This replaces the M24 models from Carlo Gavazzi and allows to use MEC meter as grid meter.

## Install ##
Clone into /data/
To start the script on startup. Victron allows a start hook in /data/rc.local, see https://www.victronenergy.com/live/ccgx:root_access.
Add /data/victron_mec_meter/start_mecmeter to /data/rc.local.
```
#!/bin/bash

(cd /data/victron_mec_meter/ && ./start_mec_meter)
```

Edit mec.ini and add your credentials
