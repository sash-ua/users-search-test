from search.utils.map_data import normalize_phone_for_search

def test_normalize_phone_for_search_digits_only():
    assert normalize_phone_for_search("(+1) 202-555-0183 ext.45") == "1202555018345"
