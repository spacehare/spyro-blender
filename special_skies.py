class Sky:
    def __init__(self, name: str, /, manual: bool = False, is_sphere: bool = False):
        self.name = name
        self.is_sphere = is_sphere  # spheres: render -Z, don't extrude
        self.manual = manual  # skies that needed manual touch-ups


def quake_ok_name(name: str):
    return name.replace(' World', '').replace(' ', '_').replace("'", '').lower()


skies = [
    Sky("Alpine Ridge"),
    Sky("Aquaria Towers"),
    Sky("Artisan's World"),
    Sky("Autumn Plains World", manual=True),  # extrusion not uniform color, made an extra edge loop to tighten the vertex colors
    Sky("Beast Maker's World"),
    Sky("Blowhard"),
    Sky("Breeze Harbor", manual=True),  # non-manifold edge toward +X, "merge at last" back into place. also rotate a saturn-like planet's ring to stop z-fighting
    Sky("Canyon Speedway", manual=True),  # non uniform color on extrusion; repainted it
    Sky("Cliff Town"),
    Sky("Cloud Temples"),
    Sky("Colossus"),
    # Sky("Crush's Dungeon") # ignore because its just one color
    Sky("Crystal Flight"),
    Sky("Crystal Glacier"),
    Sky("Dark Hollow"),
    Sky("Dark Passage", is_sphere=True),
    Sky("Doctor Shemp"),
    Sky("Dragon Shores"),
    Sky("Dream Weaver's World", is_sphere=True),
    Sky("Dry Canyon"),
    Sky("Fracture Hills"),
    Sky("Glimmer"),
    Sky("Gnasty Gnorc", is_sphere=True),
    Sky("Gnasty Gnorc's Hub"),
    Sky("Gnasty's Loot", manual=True),  # some kind of extrusion issue ? also fix the saturn-like planet's ring
    Sky("Gnorc Cove"),
    Sky("Gulp's Overlook", manual=True),  # extrusion not uniform color
    Sky("Haunted Towers", manual=True, is_sphere=True),  # ripped sky has some borked vert painting -- easier to fix using a Smear in Vertex Paint mode
    Sky("High Caves", manual=True),  # extrusion error ?
    Sky("Hurricos", manual=True),  # the ripped sky might have borked vert colors? i'm not confident enough to manually repaint it
    Sky("Ice Cavern"),
    Sky("Icy Flight"),
    Sky("Icy Speedway"),
    Sky("Idol Springs"),
    Sky("Jacques", is_sphere=True),
    Sky("Lofty Castle", is_sphere=True),
    Sky("Magic Crafter's World"),
    Sky("Magma Cone"),
    Sky("Main Menu"),
    Sky("Metalhead", manual=True),  # sharp verts, repainted
    Sky("Metro Speedway"),
    Sky("Metropolis"),
    Sky("Misty Bog", manual=True),  # non-manifold pair of verts, "merge at center"
    Sky("Mystic Marsh"),
    Sky("Night Flight", manual=True),  # dissolve vert on a crystal. merge another 2 verts
    Sky("Ocean Speedway", manual=True),  # strange sharp colors under clouds
    Sky("Peace Keeper's World"),
    Sky("Ripto's Arena"),
    Sky("Robotica Farms"),
    Sky("Scorch"),
    Sky("Shady Oasis"),
    Sky("Skelos Badlands"),
    Sky("Stone Hills"),
    Sky("Summer Forest World"),
    Sky("Sunny Beach"),
    Sky("Sunny Flight"),
    Sky("Terrace Village"),
    Sky("Toasty"),
    Sky("Town Square", manual=True),  # "merge at center" on 2 pairs of verts
    Sky("Tree Tops", manual=True),  # extrusion error on tree extras
    Sky("Twilight Harbor", manual=True),  # extrusion issue ? not sure how to diagnose it, so im just manually doing the extrusion steps myself
    Sky("Wild Flight"),
    Sky("Winter Tundra World"),
    Sky("Wizard Peak"),
    Sky("Zephyr"),
]
