async def toggle_antispam(config, value: bool):
    config["enabled"] = value
