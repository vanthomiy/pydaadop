from bson import ObjectId

from pydaadop.queries.base.base_list_filter import BaseListFilter


def test_objectid_values_kept():
    oid = ObjectId()
    flt = BaseListFilter([oid], key="_id")
    mongo = flt.to_mongo_filter()
    assert "$in" in mongo["_id"]
    assert isinstance(mongo["_id"]["$in"][0], ObjectId)


def test_hex_string_converted_by_default():
    oid = ObjectId()
    hex_str = str(oid)
    flt = BaseListFilter([hex_str], key="_id")
    mongo = flt.to_mongo_filter()
    assert isinstance(mongo["_id"]["$in"][0], ObjectId)


def test_hex_string_not_converted_when_disabled():
    oid = ObjectId()
    hex_str = str(oid)
    flt = BaseListFilter([hex_str], key="_id")
    mongo = flt.to_mongo_filter(convert_objectid=False)
    assert isinstance(mongo["_id"]["$in"][0], str)


def test_non_hex_string_kept():
    s = "this-is-not-an-objectid"
    flt = BaseListFilter([s], key="_id")
    mongo = flt.to_mongo_filter()
    assert isinstance(mongo["_id"]["$in"][0], str)
