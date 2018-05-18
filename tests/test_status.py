from pytz import timezone

from bin.bb8.status import interpret_timestamp_output


def test_that_empty_timestamp_is_interpreted_as_missing_data():
    x = interpret_timestamp_output("".encode("utf-8"))
    assert x == "No files present"


def test_that_timestamp_is_correctly_parsed_and_zoned():
    input = "2018-05-18T15:00:00 +0200"
    # Going from +2 to -5 timezone
    x = interpret_timestamp_output(input.encode("utf-8"),
                                   timezone=timezone("America/Jamaica"))
    assert x == "2018-05-18 08:00:00-05:00"
