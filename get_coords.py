import requests
import argparse

def get_pdb(pdb_id):
    """
    Fetch the PDB file content as a string from RCSB PDB.
    Raises an error if the fetch fails.
    """
    pdb_id = pdb_id.upper().strip()

    url = f"https://files.wwpdb.org/download/{pdb_id}.pdb"
    r = requests.get(url, timeout=60)
    print(f"GET {url} -> {r.status_code}")
    return r.text

def get_p_coords(rna_structure):
    p_coords = []
    for line in rna_structure.splitlines():
        if line.startswith("ATOM") and "P" in line[13:14]:
            parts = line.split()
            x = float(line[30:38].strip())
            y = float(line[38:46].strip())
            z = float(line[46:54].strip())
            p_coords.append((x, y, z))
    return p_coords

def get_ca_coords(protein_structure, chain):
    ca_coords = []
    for line in protein_structure.splitlines():
        if line.startswith("ATOM") and "CA" in line[13:15] and line[21:22] == chain:
            parts = line.split()
            x = float(line[30:38].strip())
            y = float(line[38:46].strip())
            z = float(line[46:54].strip())
            ca_coords.append((x, y, z))
    return ca_coords

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get backbone coordinates from PDB")
    parser.add_argument("--pdb_id", help="PDB ID")
    parser.add_argument("--chain", help="Chain identifier for protein (required if type is protein)")
    parser.add_argument("--pdb_file", help="Path to local PDB file (optional)")
    parser.add_argument("--type", choices=["rna", "protein"], help="Type of structure to extract coordinates from")
    args = parser.parse_args()

    if args.pdb_file:
        with open(args.pdb_file, "r") as f:
            structure = f.read()
            protein_name = args.pdb_file.split("/")[-1].split(".")[0]
            chain = args.chain if args.chain else "A"
    else:
        protein_name = args.pdb_id
        structure = get_pdb(protein_name)

    if args.type == "rna":
        coords = get_p_coords(structure)
    else:
        coords = get_ca_coords(structure, chain)

    with open(f"{protein_name}_{args.type}_coords.txt", "w") as f:
        for coord in coords:
            f.write(f"{coord[0]} {coord[1]} {coord[2]}\n")
    print(f"Wrote {len(coords)} {args.type} atom coordinates to {protein_name}_{args.type}_coords.txt")