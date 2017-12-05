import pytest
import mock
import warnings
from apis import user_event_rsvpd
from apis import save_rsvp

@pytest.mark.django_db
def test_save_rsvp():
    funrun_event = Event.get(title='FunRun 5k')
    user = User.get(username='vpeters')
    status = user_event_rsvpd(user_id=user.id, event_id=funrun_event.id)
    if not status:
        save_rsvp(user_id=user.id, event_id=funrun_event.id)
        assert user_event_rsvpd(user_id=user.id, event_id=funrun_event.id), \
            "User vpeters not RSVP'd to event after running save_rsvp"
        remove_rsvp(user_id=user.id, event_id=funrun_event.id)
    else:
        warnings.warn("User vpeters already RSVP'd to event.")
        warnings.warn("Removing RSVP before testing save_rsvp.")
        remove_rsvp(user_id=user.id, event_id=funrun_event.id)
        save_rsvp(user_id=user.id, event_id=funrun_event.id)
        assert user_event_rsvpd(user_id=user.id, event_id=funrun_event.id), \
            "User vpeters not RSVP'd to event after running save_rsvp"
        remove_rsvp(user_id=user.id, event_id=funrun_event.id)
