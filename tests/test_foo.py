import requests
from pytest import mark

from program.models import Speaker


@mark.django_db
def test_sanity_check():
    """
    Sanity check on the test setup to see if everything works as expected.
    """
    Speaker.objects.create()
    s = Speaker.objects.get()
    assert s.full_name == ""
    assert s.order == 500
    assert Speaker.objects.count() == 1
