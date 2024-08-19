import pytest

from sylva.helpers.nlp import NatLangProcessor

nlp = NatLangProcessor()


@pytest.mark.parametrize('prompt,response', [
    ('I live in Boston', 'Boston'),
    ('I used to live in Boston, longer sentence', 'Boston'),
    ('I lived in Boston then', 'Boston'),
    ('I\'ve lived in Boston before', 'Boston'),
    ('I grew up in Boston', 'Boston'),
    ('I was born in Boston', 'Boston'),
    ('I moved to Boston', 'Boston'),
    ('I am moving to Boston', 'Boston'),
    ('I\'m moving to Boston', 'Boston'),
    ('I am based in Boston', 'Boston'),
    ('I\'m based out of Boston', 'Boston'),
    ('I am living in Boston', 'Boston'),
    ('I\'m living in Boston', 'Boston'),
    ('I was living in Boston', 'Boston'),
    ('I hail from Boston', 'Boston'),
    ('I am hailing from Boston', 'Boston'),
])
def test_single_residency(prompt, response):
    """Test a single residency query"""
    assert nlp.get_residences(prompt) == [response]


@pytest.mark.xfail(reason='NLP does not yet properly handle multiple residencies', strict=False)
@pytest.mark.parametrize('prompt,response', [
    ('I\'ve lived in both Boston and Bremen before', ['Boston', 'Bremen']),
    ('I\'ve vacationed in Manchester, but lived in Bremen and Boston', ['Bremen', 'Boston']),
    ('I used to live in Boston, but I now live in Bremen', ['Boston', 'Bremen']),
    ('I used to live in Boston, but I moved to Bremen', ['Boston', 'Bremen']),
    ('I\'ve lived in Boston, vacationed in Enble, and moved to Bremen', ['Boston', 'Bremen']),
])
def test_multiple_residency(prompt, response):
    """Test multiple residency queries"""
    assert set(nlp.get_residences(prompt)) == set(response)


@pytest.mark.parametrize('prompt', [
    ('I\'ve vacationed in Enble'),
    ('I vacationed in both Bostom and Bremen'),
])
def test_non_residency(prompt):
    """Test non-residency queries"""
    assert nlp.get_residences(prompt) == []


@pytest.mark.parametrize('prompt', [
    ('He lives in Boston'),
])
def test_non_self_residency(prompt):
    """Test non-self residency queries"""
    assert nlp.get_residences(prompt) == []


def test_empty_prompt():
    """Test empty prompt for empty response"""
    assert nlp.get_residences('') == []


@pytest.mark.parametrize('prompt', [
    (123),
    (None),
    (True),
    (['abc', 'def']),
])
def test_invalid_prompt_type(prompt):
    """Affirm that an exception is raised for invalid prompt types"""
    with pytest.raises(TypeError):
        nlp.get_residences(prompt)

