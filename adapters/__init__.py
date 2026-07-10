from . import real_estate, recruiting

ADAPTERS = {"real_estate": real_estate.adapter, "recruiting": recruiting.adapter}


def load(name: str):
    if name not in ADAPTERS:
        raise KeyError(f"未知のアダプタ: {name}")
    return ADAPTERS[name]()
