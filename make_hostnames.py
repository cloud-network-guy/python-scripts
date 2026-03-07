#!/usr/bin/env python3

HOSTNAMES = [
    "runtime", "runtime-preview", "content", "content-preview",
    "ui-authoring","lscs-runtime", "lsds-runtime", "otds",
    "argocd"
]


def make_hostnames (domain: str):
    
    output = ""
    for i, hostname in enumerate(HOSTNAMES):
        output += f"{hostname}.{domain}"
        output += "" if i == len(HOSTNAMES)-1 else ", "
    return output


if __name__ == "__main__":

    from sys import argv

    domain = argv[1] if len(argv) > 1 else "nowhere.net"
    _ = make_hostnames(domain)
    print(_)
