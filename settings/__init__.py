from . import settings_addon, settings_main


def register():
    settings_addon.register()
    settings_main.register()


def unregister():
    settings_main.unregister()
    settings_addon.unregister()
