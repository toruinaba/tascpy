from tascpy.core.names import missing_message, normalize, suggest


def _items(*names):
    return [(n, n, n) for n in names]


def test_normalize_absorbs_width_case_and_spaces():
    assert normalize("ＳＧ１　荷重（kN）") == "sg1 荷重(kn)"
    assert normalize("  a\t b ") == "a b"


def test_suggest_orders_exact_then_similar_then_partial():
    candidates = _items("荷重 (kN)", "荷重2", "変位", "SG1", "SG10")
    assert suggest("荷重（ｋＮ）", candidates) == ["荷重 (kN)"]
    assert suggest("ｓｇ１", candidates) == ["SG1", "SG10"]
    assert suggest("荷重", candidates) == ["荷重2", "荷重 (kN)"]
    assert suggest("x", candidates) == []
    assert suggest("", candidates) == []


def test_suggest_ignores_single_char_candidates_contained_in_key():
    # 1文字の候補は key の部分文字列であっても候補にしない
    assert suggest("SG12", _items("1", "2")) == []
    assert suggest("1", _items("@1", "@12")) == ["@1", "@12"]


def test_suggest_keeps_best_candidate_per_target():
    # 列名とチャンネル名の両方で当たる列は、順位の高い方の表示だけを残す
    candidates = [("c", "'c'", "c"), ("CH1", "'c'（ch 'CH1'）", "c"), ("ch10", "'d'（ch 'ch10'）", "d")]
    assert suggest("ch1", candidates) == ["'c'（ch 'CH1'）", "'d'（ch 'ch10'）"]
    assert suggest("C", candidates) == ["'c'", "'d'（ch 'ch10'）"]
    assert suggest("a", _items("a", "ab", "abc"), n=2) == ["a", "ab"]


def test_missing_message():
    assert missing_message("列", "q", _items("a")) == "列 'q' が存在しません"
    assert missing_message("列", "A", _items("a")) == "列 'A' が存在しません（候補: a）"
