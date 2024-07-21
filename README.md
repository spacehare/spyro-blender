# spyro-blender

convert spyro skies into quake-compatible skyboxes

---

folder path example = `N:\SteamLibrary\steamapps\common\Blender\4.1\scripts\addons\rabbit`

---

manual fix generic steps (also see fixed_skyboxes.blend):

- CTRL J = join objects
- M B = merge verts by 0.0005 distance
- E Z -10 = extrude base of domes
- S Z 0 = then scale z to 0 to flatten it
- F (F2 addon) = create new face from bottom edge loop, if sky is a dome

dealing with extra geo...

- CTRL+L = select linked
- P S = separate by selection
- move extraneous geo to separate Extras view layer (stars, planets, etc)
- composite extraneous geo over dome/sphere sky
- Scene -> Render -> Film: Transparent
- Render Engine: Workbench
- Lighting: Flat
- Color: Attribute
- (then we don't even need a shader!)
