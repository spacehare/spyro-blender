class Sky:
    def __init__(self, name: str, /, manual: bool = False, is_sphere: bool = False):
        self.name = name
        self.is_sphere = is_sphere
        self.manual = manual


skies = [
    # skies that needed manual touch-ups
    # Sky("Crush's Dungeon") # ignore because its just one color
    Sky("Breeze Harbor", manual=True),  # non-manifold edge toward +X, "merge at last" back into place. also rotate a saturn-like planet's ring to stop z-fighting
    Sky("Gnasty's Loot", manual=True),  # some kind of extrusion issue ? also fix the saturn-like planet's ring
    Sky("Misty Bog", manual=True),  # non-manifold pair of verts, "merge at center"
    Sky("Night Flight", manual=True),  # dissolve vert on a crystal. merge another 2 verts
    Sky("Town Square", manual=True),  # "merge at center" on 2 pairs of verts
    Sky("Twilight Harbor", manual=True),  # extrusion issue ? not sure how to diagnose it, so im just manually doing the extrusion steps myself
    Sky("Autumn Plains World", manual=True),  # extrusion not uniform color, made an extra edge loop to tighten the vertex colors
    Sky("Gulp's Overlook", manual=True),  # extrusion not uniform color
    Sky("Hurricos", manual=True),  # the ripped sky might have borked vert colors? i'm not confident enough to manually repaint it
    Sky("Haunted Towers", manual=True),  # ripped sky has some borked vert painting -- easier to fix using a Smear in Vertex Paint mode
    Sky("High Caves", manual=True),  # extrusion error ?
    Sky("Canyon Speedway", manual=True),  # non uniform color on extrusion; repainted it
    Sky("Metalhead", manual=True),  # sharp verts, repainted
    Sky("Ocean Speedway", manual=True),  # strange sharp colors under clouds
    Sky("Tree Tops", manual=True),  # extrusion error on tree extras

    # spheres: render -Z, don't extrude
    Sky("Jacques", is_sphere=True),
    Sky("Lofty Castle", is_sphere=True),
    Sky("Dark Passage", is_sphere=True),
    Sky("Dream Weaver's World", is_sphere=True),
    Sky("Gnasty Gnorc", is_sphere=True),
    Sky("Haunted Towers", is_sphere=True),
]
