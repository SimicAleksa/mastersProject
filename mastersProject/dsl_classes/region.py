class Region:
    def __init__(self, name, portrayal):
        self.name = name
        self.portrayal = portrayal
        self.items = {}
        self.connections = {}
        self.requirements = []
        self.environmental_dmg = None

    def add_requirements(self, requirement):
        self.requirements.append(requirement)

    def add_environmental_dmg(self, environmental_dmg):
        self.environmental_dmg = environmental_dmg

    def add_item(self, item):
        self.items[item.name] = item

    def remove_item(self, item):
        del self.items[item]

    def is_item_contained(self, item):
        return item in self.items

    def add_connection(self, direction, target_region):
        self.connections[direction] = target_region

    def print_self(self):
        items = ""
        for item in self.items:
            items += item + ", "
        items = items[:-2]
        text = f"You are in {self.portrayal}. "
        if items:
            text += f"Inside you see {items}. "
        return text

    def print_requirements(self):
        reqs = ""
        for req in self.requirements:
            reqs += str(req.item) + ", "
        reqs = reqs[:-2]
        return reqs
