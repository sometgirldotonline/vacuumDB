# vacuumDB
An esoteric database that instead of aiming for compression and functional simplicity, goes the complete other way.
It currently has no bindings for programming languages yet, it is interacted entireley in the terminal.
Call the script with any of the following arguments

### `ls`
show all the data from the table, you can add --json to get a json output

### `cloudsyncPush` and `cloudsyncPull`
Self explanatory, but this being esoteric, these do fuck all

### `vt`
Load the void telemetery dashboard. The dashboard is entirely static and just there because it is

### `add`
Adds an item. You can specify an item type with `-t item`. Providng column values comes after `-f`, in key value pairs (anything after `-f` is expected to be a k=v pair)

### `get`
Retrieve an item by its ID.

### `rm`
Remove an item by its ID

### `help`
displays help


### Specifying a database file
Defaults to DEFAULT.vdb in the current working dir if there is no .vdb or more than one. If there is only a single .vdb it will use that, otherwise you can specify a file by doing `--db=database file`


I'll be real I haven't fully tested all of this yet.
