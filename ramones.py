from collections import Counter

RAMONES = [
    {'alias': "Joey", 'real_name': "Jeffrey Hyman", 'role': "vocals"},
    {'alias': "Johnny", 'real_name': "John Cummings", 'role': "guitar"},
    {'alias': "DeeDee", 'real_name': "Douglas Colvin", 'role': "bass"},
    {'alias': "Tommy", 'real_name': "Thomas Erdelyi", 'role': "drums"},
    {'alias': "Marky", 'real_name': "Marc Bell", 'role': "drums"},
]

aliases_with_roles = {r['alias']:r['role'] for r in RAMONES}
print([f"{k} -> {v}" for k, v in aliases_with_roles.items()])

roles = [ramone['role'] for ramone in RAMONES]
print("Multiple Ramones for these roles:", [k for k, v in Counter(roles).items() if v > 1])