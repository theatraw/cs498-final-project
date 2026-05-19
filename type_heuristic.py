import pandas as pd

df = pd.read_csv("sat400_complete.csv")

def infer_category(instance):
    n = instance.lower()

    random_keywords = [
        "uf",
        "uuf",
        "rand",
        "random",
        "sgen",
        "rbsat",
        "new-difficult",
        "satsgi",
        "srhd",
        "connm",
    ]

    industrial_keywords = [
        "pipe",
        "hash",
        "context",
        "table",
        "timetable",
        "model",
        "oisc",
        "fp",
        "sqlite",
        "routing",
        "verification",
        "sll",
        "kernel",
        "scheduler",
        "crypto",
        "ascon",

        "satcoin",
        "fileobject",
        "lzmafile",
        "os_fwalk",
        "php",
        "twitter",
        "preimage",
        "goldberg",
        "shift1add",

        "alien",
        "sat_dat",
        "klieber",
        "mchess",
        "mod4block",
        "goldcrest",
        "ibm_fv",
        "ibm-",
        "aes",
        "ferry",
        "posixpath",
        "smt2",
        "cvc4",
        "em_",
        "g2-",
        "gzipfile",
        "collections_namedtuple",
        "bz2file",
        "rovers",
        "grain",
        "vmpc",
    ]

    crafted_keywords = [
        "graph",
        "grid",
        "color",
        "cover",
        "queen",
        "sudoku",
        "latin",
        "pigeon",
        "clique",
        "matching",
        "dominating",
        "tseitin",
        "prp",
        "er_",
        "stb_",

        "brent",
        "grs",
        "intervals",
        "scpc",
        "ws_",
        "divs",
        "divu",
        "satch2ways",
        "trig",

        "eqspct",
        "rook",
        "mrpp",
        "schur",
        "spg",
        "tph",
        "crafted",

        "jkkk",
        "minxor",
        "patat",
        "46bits",
        "cnp-",
        "c208",
        "ncc_",
    ]

    if any(k in n for k in random_keywords):
        return "random"

    elif any(k in n for k in industrial_keywords):
        return "industrial"

    elif any(k in n for k in crafted_keywords):
        return "crafted"

    else:
        return "unknown"


# apply once per unique instance
inst_df = (
    df[["instance"]]
    .drop_duplicates()
    .copy()
)

inst_df["category"] = inst_df["instance"].apply(infer_category)

inst_df.to_csv("sat400_results_categorized.csv", index=False)

print("Saved sat400_results_categorized.csv")

# inspect results
print(inst_df["category"].value_counts())

print("\n=== RANDOM ===")
print(inst_df[inst_df["category"] == "random"]["instance"].head(20).to_string(index=False))

print("\n=== INDUSTRIAL ===")
print(inst_df[inst_df["category"] == "industrial"]["instance"].head(20).to_string(index=False))

print("\n=== CRAFTED ===")
print(inst_df[inst_df["category"] == "crafted"]["instance"].head(20).to_string(index=False))

print("\n=== UNKNOWN ===")
print(inst_df[inst_df["category"] == "unknown"]["instance"].head(50).to_string(index=False))
