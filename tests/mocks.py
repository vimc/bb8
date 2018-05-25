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
    "user": "jean",
    "addr": "paris",
    "backup_location": "starport"
}

mock_instance_guid = "1234"


def mock_settings(targets=None):
    targets = targets or []
    return Dynamic("settings",
                   instance_guid=mock_instance_guid,
                   starport=mock_starport_settings,
                   targets=targets)


def mock_remote_paths():
    def data(include_host=False):
        p = "some/path/datadata/"
        if include_host:
            p = "server:" + p
        return p

    def meta(include_host=False):
        p = "some/path/metadata/"
        if include_host:
            p = "server:" + p
        return p

    return Dynamic("remote_paths",
                    host="host",
                    data=data,
                    meta=meta)
