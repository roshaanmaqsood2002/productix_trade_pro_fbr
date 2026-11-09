import json

BASE = "apps/productix_trade_pro_fbr/productix_trade_pro_fbr/productix_trade_pro_fbr/doctype"


def edit(name, fn):
    p = f"{BASE}/{name}/{name}.json"
    d = json.load(open(p))
    d["permissions"] = fn(d["permissions"])
    with open(p, "w") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def settings(perms):
    out = []
    for x in perms:
        if x["role"] == "TPF Operator":
            continue
        if x["role"] == "TPF Admin":
            x.update({"write": 0, "create": 0, "delete": 0, "export": 0})
        out.append(x)
    return out


def logs(perms):
    for x in perms:
        x.update({"write": 0, "create": 0})
        if x["role"] != "System Manager":
            x.update({"delete": 0, "export": 0})
    return perms


edit("tpf_settings", settings)
edit("tpf_fbr_log", logs)
print("done")