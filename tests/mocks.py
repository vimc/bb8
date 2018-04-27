class Dynamic(object):
    def __init__(self, label, **kwargs):
        self.label = label
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return str(self.label)


def mock_target(id, backup=True, restore=True, **kwargs):
    return Dynamic(id, id=id, mount_id="mount-{}".format(id),
                   name="name-{}".format(id),
                   options=Dynamic("opt", backup=backup, restore=restore),
                   **kwargs)


mock_starport_settings = {
    "user": "clark",
    "addr": "metropolis",
    "backup_location": "daily_planet"
}


def mock_settings(targets=None):
    targets = targets or []
    return Dynamic("settings",
                   starport=mock_starport_settings,
                   targets=targets)


