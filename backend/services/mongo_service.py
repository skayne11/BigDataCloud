from etl.load_mongo import list_all, find_by_name

def get_all_satellites():
    try:
        docs = list_all()
        # convert any non-serializable fields if necessary
        return docs
    except Exception as e:
        print("Error mongo get_all:", e)
        return []

def get_satellite_by_name(name):
    try:
        return find_by_name(name)
    except Exception as e:
        print("Error mongo find:", e)
        return None
