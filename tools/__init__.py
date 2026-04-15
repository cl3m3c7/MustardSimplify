from . import ops_data_removal, ops_fast_normals


def register():
    ops_data_removal.register()
    ops_fast_normals.register()


def unregister():
    ops_fast_normals.unregister()
    ops_data_removal.unregister()
