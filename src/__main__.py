import argparse
import sys
import pickle
import json
import glob
import os
import datalayer
import inflater
import tabulate

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

    add_parser = subparsers.add_parser("add", help="Add a name and value")
    add_parser.add_argument(
        "-f", "--fields",
        nargs="+",          # one or more kv pairs
        metavar="key=val",
        help="Fields to insert"
    )

    get_parser = subparsers.add_parser("get", help="Get the data associated with a id")
    get_parser.add_argument("id", help="ID to retrieve data for")
    
    rm_parser = subparsers.add_parser("rm", help="Remove an item")
    rm_parser.add_argument("id", help="ID to remove")

    help_parser = subparsers.add_parser("help", help="Display help information")
    args = parser.parse_args()
    
    dbpath =  resolve_db(args.db)
    db = datalayer.get(dbpath)
    

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
            fields = {}
            for kv in args.fields or []:
                if "=" not in kv:
                    raise ValueError(f"Invalid field format: {kv}")
                k, v = kv.split("=", 1)
                if k not in db["cols"]:
                    db["cols"].append(k)
                    sys.stderr.write(f"added one new column to the database: {k}\n")
                fields[k]=v
            db["data"].append(fields)
            datalayer.store(db, dbpath)
            sys.stderr.write(f"Added one new item to the database. ID: {len(db['data']) - 1}\n")
            sys.stdout.write(str(len(db['data'])-1))
        case "get":
            sys.stdout.write(json.dumps(db['data'][int(args.id)]))
        case "rm":
            args.id = int(args.id)
            db["data"][args.id] = inflater.return_obf_bloat("deletes your file cutely :3 nya paws at you")
            db["deleted"].append(args.id)
            datalayer.store(db, dbpath)
        case _:
            parser.print_help()    


if __name__ == "__main__":
    main()
