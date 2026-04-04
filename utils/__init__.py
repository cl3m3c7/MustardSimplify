from . import execution_time, ops_link, ops_reset


def register():
    ops_link.register()
    ops_reset.register()
    execution_time.register()


def unregister():
    execution_time.unregister()
    ops_reset.unregister()
    ops_link.unregister()
