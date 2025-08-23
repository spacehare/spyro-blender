def quake_ok_name(name: str):
    return name.replace(' ', '_').replace("'", '').lower()
