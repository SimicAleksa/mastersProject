DIRECTIONS = [
    "move N",
    "move E",
    "move S",
    "move W"
]

POSSIBLE_COMMANDS = [
    "move N",
    "move S",
    "move W",
    "move E",
    "drop <item>",
    "open <item>",
    "take <item>",
    "use <item>",
    "equip <item>",
    "unequip <item>",
    "info <item>",
    "inventory",
    "health",
    "attack",
    "flee",
    "inc vigor",
    "inc endurance",
    "inc strength",
    "inc intelligence",
    "stats"
]


def display_help():
    help_string = "List of possible commands: \n"
    for command in POSSIBLE_COMMANDS:
        help_string += command + "\n"
    print(help_string[:-1])
