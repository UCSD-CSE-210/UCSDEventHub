import pytest
import mock

from apis import user_event_rsvpd

@pytest.mark.django_db
def test_chk_user_event_rsvpd():
    check_rsvp_for_admin = user_event_rsvpd(1,1)
    assert not check_rsvp_for_admin, "Admin is not rsvpd to event 1"