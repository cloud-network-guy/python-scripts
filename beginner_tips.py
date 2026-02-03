from collections import Counter

RAMONES = [
    {'alias': "Joey", 'real_name': "LKj", 'role': "vocals"},
    {'alias': "Johnny", 'real_name': "LKj", 'role': "guitar"},
    {'alias': "DeeDee", 'real_name': "LKj", 'role': "bass"},
    {'alias': "Tommy", 'real_name': "LKj", 'role': "drums"},
    {'alias': "Marky", 'real_name': "LKj", 'role': "drums"},
]

roles = [ramone['role'] for ramone in RAMONES]

aliases = {r['alias']:r['role'] for r in RAMONES}
print([f"{k} -> {v}" for k, v in aliases.items()])

_ = Counter(roles)
print("Multiple ramones for these roles:", [k for k, v in _.items() if v > 1])