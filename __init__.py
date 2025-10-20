from .dev import RegisterAll, UnregisterAll


def register():
    RegisterAll()


def unregister():
    UnregisterAll()


if __name__ == "__main__":
    register()
