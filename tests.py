
def test_hello_util():
    from requests_html import hello_util
    assert hello_util('World') == 'Hello, World!'
