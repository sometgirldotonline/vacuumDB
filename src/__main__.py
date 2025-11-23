import argparse
import sys
import pickle
import datetime
import json
import glob
import os
import datalayer
import inflater
import tabulate
import random 
from dicewarepy import diceware
import time


# metadatas
class ItemTypes:
    class Paper:
        decayson = "time"
        fake_chunks = 0
        time = 518400  # 6 days
        @classmethod
        def decay(cls, data):
            now = time.time()
            age = now -  data["meta"].get("cdate", now)
            decayFrac = min(age / cls.time, 1.0)
            newData = data.copy()
            
            for k,v in newData.items():
                if k == "meta":
                    continue
                else:
                    if isinstance(v, str):
                        m = list(v)
                        for i in range(len(m)):
                            if random.random() < decayFrac:
                                m[i] = chr(random.randint(33,126))
                        newData[k] = "".join(m)
            return newData
    class StoneTablet:
        fake_chunks = 3
        time = 315360000  # 10 years
        decayson = "accessadd"
        @classmethod
        def decay(cls, data):
            now = time.time()
            age = now -  data["meta"].get("cdate", now)
            decayFrac = min(age / cls.time, 1.0)
            
            newData = data.copy()
            
            for k,v in newData.items():
                if k == "meta":
                    continue
                else:
                    if isinstance(v, str):
                        m = list(v)
                        for i in range(len(m)):
                            if random.random() < decayFrac:
                                m[i] = " "
                        newData[k] = "".join(m)
            return newData

    class MetalPlate:
        decayson = "time"
        fake_chunks = 2
        time = 31536000000  # ~1,000 years
        @classmethod
        def decay(cls, data):
            return data

    class HumanBrain:
        decayson = "add"
        fake_chunks = 1
        time = 2240543592  # 71 years
        @classmethod
        def decay(cls, data):
            now = time.time()
            age = now -  data["meta"].get("cdate", now)
            decayFrac = min(age / cls.time, 1.0)
            
            newData = data.copy()
            
            for k,v in newData.items():
                if k == "meta":
                    continue
                else:
                    if isinstance(v, str):
                        m = v.split(" ")
                        for i in range(len(m)):
                            if random.random() < decayFrac:
                                m[i] = ""
                        newData[k] = " ".join(m)
            return newData
    class roadkill:
        decayson = "time"
        fake_chunks = 5
        time = 1210000 # two weeks
        @classmethod
        def decay(cls, data):
            now = time.time()
            age = now -  data["meta"].get("cdate", now)
            decayFrac = min(age / cls.time, 1.0)
            
            newData = data.copy()
            
            for k,v in newData.items():
                if k == "meta":
                    continue
                else:
                    if isinstance(v, str):
                        m = v.split(" ")
                        for i in range(len(m)):
                            if random.random() < decayFrac:
                                m[i] = "fly buzzes"
                        newData[k] = " ".join(m)
            return newData
    class leFishe:
        decayson = "time"
        fake_chunks = 1
        time = 60  # a fucking minute
        @classmethod
        def decay(cls, data):
            now = time.time()
            age = now -  data["meta"].get("cdate", now)
            decayFrac = min(age / cls.time, 1.0)
            
            newData = data.copy()
            
            for k,v in newData.items():
                if k == "meta":
                    continue
                else:
                    if isinstance(v, str):
                        m = v.split(" ")
                        for i in range(len(m)):
                            if random.random() < decayFrac:
                                m[i] = "blub"
                        newData[k] = " ".join(m)
            return newData
    class MotherfuckingAir:
        fake_chunks = 0
        time = 0
        decayson = "time"
        def decay(cls,data):
            return data

itemtypeeffects = {
    "paper": ItemTypes.Paper,
    "stoneTablet": ItemTypes.StoneTablet,
    "metalPlate": ItemTypes.MetalPlate,
    "brain": ItemTypes.HumanBrain,
    "air": ItemTypes.MotherfuckingAir,
    "leFishe": ItemTypes.leFishe,
    "roadkill": ItemTypes.roadkill
}


def fakeprogress(rmin= 0.01, rmax= 0.3):
    progress = 0
    maxProgress = 100
    
    while progress <= maxProgress:
        bar = '#' * (progress // 2) + '-' * ((maxProgress - progress) // 2)
        sys.stdout.write(f'\r[{bar}] {progress}%')
        sys.stdout.flush()
        progress += 1;
        
        delay = random.uniform(0.01, 0.3)
        time.sleep(delay)


# find the DB file specified
def resolve_db(path_arg):
    # If user explicitly passed --db, use that
    if path_arg:
        return path_arg

    # Otherwise scan for local .vdb files
    vdb_files = glob.glob("*.vdb")

    if len(vdb_files) == 1:
        return vdb_files[0]

    # 0 or >1 → fallback
    if not(os.path.isfile("DEFAULT.vdb")):
        # it dont exist probably idk
        datalayer.store({
            "cols":[],
            "data": [],
            "deleted": []
        }, "DEFAULT.vdb")
    
    
    return "DEFAULT.vdb"
def serialize_bytes(obj):
    if isinstance(obj, bytes):
        return f"bytes[{len(obj)}]"
    raise TypeError(f"Type {type(obj)} not serializable")

def main():
    """
    Main function for vdb
    """

    # 1. Argument Parsing
    parser = argparse.ArgumentParser(description="vaccumdb - vdb. v1")
    parser.add_argument(
        "--db",
        help="Path to the .vdb database file",
        default=None
    )

    # Subcommands
    subparsers = parser.add_subparsers(title="subcommands", dest="command", help="Available subcommands")

    ls_parser = subparsers.add_parser("ls", help="Get all data in a table format or JSON format (use --json)")
    ls_parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    add_parser = subparsers.add_parser("cloudsyncPush", help="Push data to cloud")
    add_parser = subparsers.add_parser("cloudsyncPull", help="Pull data from cloud")
    add_parser = subparsers.add_parser("vt", help="Log into the Void Telemetery Dashboard")
    add_parser = subparsers.add_parser("add", help="Add a name and value")
    add_parser.add_argument(
        "-f", "--fields",
        nargs="+",          # one or more kv pairs
        metavar="key=val",
        help="Fields to insert"
    )
    add_parser.add_argument(
        "-t", "--type",
        help="one of the normal itemtypes"
    )
    get_parser = subparsers.add_parser("get", help="Get the data associated with a id")
    get_parser.add_argument("id", help="ID to retrieve data for")
    
    rm_parser = subparsers.add_parser("rm", help="Remove an item")
    rm_parser.add_argument("id", help="ID to remove")

    help_parser = subparsers.add_parser("help", help="Display help information")
    args = parser.parse_args()
    
    dbpath =  resolve_db(args.db)
    db = datalayer.get(dbpath)
    
    # check deathtimes of datas
    
    for i in range(len(db["data"])):
        if i not in db["deleted"]:
            if time.time() - db["data"][i]["meta"]["cdate"] > db["data"][i]["meta"]["material"].time:
                print(f"Item #{i} expired. Sorry.")
                db["data"][i] = "expawred"
                db["deleted"].append(i)
                datalayer.store(db, dbpath)
            else:
                if args.command == "add" and db["data"][i]["meta"]["material"].decayson == "add":
                    db["data"][i]= db["data"][i]["meta"]["material"].decay(db["data"][i])
                if (args.command == "add" or args.command == "get" or args.command == "ls" or args.command == "rm") and db["data"][i]["meta"]["material"].decayson == "access":
                    db["data"][i]= db["data"][i]["meta"]["material"].decay(db["data"][i])
                if db["data"][i]["meta"]["material"].decayson == "time":
                    db["data"][i]= db["data"][i]["meta"]["material"].decay(db["data"][i])
            datalayer.store(db, dbpath)
            
    # 2. Processing (Perform actions based on arguments)

        
    match args.command:
        case "help":
            parser.print_help()
        case "ls":
            if args.json:
                
                sys.stdout.write(json.dumps(db['data'], default=serialize_bytes))
            else:
                
                print(tabulate.tabulate([
    [row.get(col, "") for col in db["cols"]]
    for i, row in enumerate(db['data'])
    if i not in db["deleted"]
]
, headers=db["cols"]))
        case "add":
            print("Choose an material type (write exactly)  ")
            if args.type == None:
                for key in itemtypeeffects.keys():
                    print(key)
                itype = itemtypeeffects[input("> ")]
            else:
                itype = itemtypeeffects[args.type]
            fields = {}
            for kv in args.fields or []:
                if "=" not in kv:
                    raise ValueError(f"Invalid field format: {kv}")
                k, v = kv.split("=", 1)
                if k not in db["cols"]:
                    db["cols"].append(k)
                    sys.stderr.write(f"added one new column to the database: {k}\n")
                fields[k]=v
            fields["meta"] = {
                "time": itype.time,
                "material": itype,
                "cdate": time.time()
            }
            db["data"].append(fields)
            datalayer.store(db, dbpath)
            sys.stderr.write(f"Added one new item to the database. ID: {len(db['data']) - 1}\n")
            sys.stdout.write(str(len(db['data'])-1))
        case "get":
            sys.stdout.write(json.dumps(db['data'][int(args.id)]))
        case "rm":
            startsize = os.path.getsize(dbpath)
            print("Deleting, pass one.")
            time.sleep(1)
            fakeprogress()
            time.sleep(1)
            print("\nDeleting, pass two.")
            time.sleep(1)
            fakeprogress(rmin=0.001, rmax=0.01)
            print("\nSending to void.")
            print(f"Transferring #{args.id} to /dev/void")
            fakeprogress(rmin=0.001, rmax=0.01)
            print("\nComplete.")
            args.id = int(args.id)
            db["data"][args.id] = "deletes your file cutely :3 nya paws at you"
            db["deleted"].append(args.id)
            datalayer.store(db, dbpath)
            print(f"Database was {startsize}B originally. Database now takes up {os.path.getsize(dbpath)}B. Your database size has changed by {((os.path.getsize(dbpath) - startsize) / startsize) * 100}% ")
        case "cloudsyncPush":
            print("Syncronising data to VDB Cloud...")
            time.sleep(0.05)
            print(datetime.datetime.now().strftime("--%Y-%m-%d %H:%M:%S--") + "   cloud.vacuumdb.com/push")
            time.sleep(0.05)
            print("Resolving cloud.vacuumdb.com (cloud.vacuumdb.com)... 420.69.420.69, 8008:8008:8008:6::200e")
            time.sleep(0.05)
            print("Connecting to cloud.vacuumdb.com (cloud.vacuumdb.com)|420.69.420.69|:420... connected.")
            time.sleep(0.05)
            print("Uploading database.vdb to https://cloud.vacuumdb.com/push")
            time.sleep(0.05)
            fakeprogress()
            time.sleep(0.05)
            print()
            print("HTTP request sent, awaiting response... 201 Created")
            print("")
            print("Data syncronised. Here is your datakey, you will need this to redownload your data.")
            print("[ "+ " ".join(diceware(n=15)) + " ]")
            print("")
            print("")
            print("")
        case "cloudsyncPull":
            dk = input("Enter your datakey:\n> ").split(" ")
            for k in dk:
                k = k.upper()
            dk = "".join(dk)
            print("Pulling data from VDB Cloud...")
            time.sleep(0.05)
            print(datetime.datetime.now().strftime("--%Y-%m-%d %H:%M:%S--") + "   cloud.vacuumdb.com/pull/"+dk)
            time.sleep(0.05)
            print("Resolving cloud.vacuumdb.com (cloud.vacuumdb.com)... 420.69.420.69, 8008:8008:8008:6::200e")
            time.sleep(0.05)
            print("Connecting to cloud.vacuumdb.com (cloud.vacuumdb.com)|420.69.420.69|:420... connected.")
            time.sleep(0.05)
            print("HTTP request sent, awaiting response... 420 OK")
            time.sleep(0.05)
            print("Length: 69Kib [application/vdb]")
            time.sleep(0.05)
            print("Saving to: /dev/null")
            fakeprogress()
            print("")
            time.sleep(0.05)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (69Gib/s) - 'data.vdb' saved [69420]")
            print("")
            time.sleep(0.05)
            print("Error: InternLLMDataGone")
            print("")
            print("")
            print("Sorry, it looks like one of our interns let an LLM run amuck in the production database again")
            print("")
            print("")
        case "vt":
            print("Getting Voidtelemetery Key")
            time.sleep(0.05)
            print(datetime.datetime.now().strftime("--%Y-%m-%d %H:%M:%S--") + "   cloud.vacuumdb.com/voidtelemetary")
            time.sleep(0.05)
            print("Resolving cloud.vacuumdb.com (cloud.vacuumdb.com)... 420.69.420.69, 8008:8008:8008:6::200e")
            time.sleep(0.05)
            print("Connecting to cloud.vacuumdb.com (cloud.vacuumdb.com)|420.69.420.69|:420... connected.")
            time.sleep(0.05)
            print("HTTP request sent, awaiting response... 420 OK")
            time.sleep(0.05)
            print("Length: 69Kib [text/plain]")
            time.sleep(0.05)
            print("Saving to: /dev/null")
            fakeprogress()
            print("")
            time.sleep(0.05)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (69Gib/s) - 'key.vt' saved [69420]")
            print("")
            time.sleep(0.05)
            print("Your void telemetary key")
            vtKa = diceware(n=6)
            vtk = "".join(w.capitalize() for w in vtKa)
            vtk = "http://vacuumdb.pages.dev/voidtelemetery/dashboard#/"+vtk
            print("╔═"+("═"*len(vtk))+"═╗")
            print("║ "+vtk+" ║")
            print("╚═"+("═"*len(vtk))+"═╝")
            
        case _:
            parser.print_help()    


if __name__ == "__main__":
    main()
