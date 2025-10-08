def register():
    from .data import Build_colormap_previews

    Build_colormap_previews()


def unregister():
    from .data import Free_colormap_previews

    Free_colormap_previews()
