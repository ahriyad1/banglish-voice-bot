from banglish import clean_output, load_prompt


def test_strips_label_and_quotes():
    assert clean_output('Banglish: "ami ashchi"') == "ami ashchi"


def test_removes_blank_lines():
    assert clean_output("ami ashchi\n\n  \ntumi kothay?  ") == "ami ashchi\ntumi kothay?"


def test_empty_is_safe():
    assert clean_output("") == ""
    assert clean_output(None) == ""


def test_prompt_loads():
    prompt = load_prompt()
    assert "Banglish" in prompt
    assert "Do not translate" in prompt
