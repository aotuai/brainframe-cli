import importlib
import sys
from unittest import mock

import pytest
from brainframe.cli.commands.utils import by_name
from brainframe.cli.commands.utils import parse_version

update_mod = importlib.import_module("brainframe.cli.commands.update")


class _Failed(Exception):
    """Raised by the mocked fail_translate so tests can see the message ID."""


def test_parse_version_valid():
    assert str(parse_version(" v1.2.3\n")) == "1.2.3"


def test_parse_version_malformed_exits_cleanly():
    with mock.patch(
        "brainframe.cli.commands.utils.print_utils.fail_translate",
        side_effect=_Failed,
    ) as fail:
        with pytest.raises(_Failed):
            parse_version("not-a-version")
    assert fail.call_args.args[0] == "general.invalid-version"


def _run(existing, requested, argv, answer=None):
    """Runs `brainframe update` with the given extra CLI arguments.

    With no arguments the command runs interactively and the requested version
    is "latest", which is resolved to `requested`.

    :return: (downloaded, asked_downgrade, failure_message_id). The kwargs
        passed to the downgrade prompt are stored in `_run.prompt_kwargs`.
    """
    argv = ["brainframe", "update"] + argv
    asked = []
    _run.prompt_kwargs = None

    def ask_yes_no(message_id, **kwargs):
        asked.append(message_id)
        if message_id == "update.ask-force-downgrade":
            _run.prompt_kwargs = kwargs
        return answer if message_id == "update.ask-force-downgrade" else False

    failure = None
    with mock.patch.object(sys, "argv", argv), mock.patch.object(
        update_mod, "config"
    ) as config, mock.patch.object(
        update_mod, "brainframe_compose", mock.MagicMock(unsafe=True)
    ) as compose, mock.patch.object(
        update_mod.print_utils, "ask_yes_no", side_effect=ask_yes_no
    ), mock.patch.object(
        update_mod.print_utils, "fail_translate", side_effect=_Failed
    ) as fail:
        config.install_path.value = mock.MagicMock()
        compose.check_existing_version.return_value = existing
        compose.get_latest_version.return_value = requested
        try:
            by_name["update"]()
        except _Failed:
            failure = fail.call_args.args[0]
        return (
            compose.download.called,
            "update.ask-force-downgrade" in asked,
            failure,
        )


def _noninteractive(requested, *extra):
    return ["--noninteractive", "--version", requested, *extra]


def test_noninteractive_downgrade_blocked_without_force():
    result = _run("2.0.0", "1.0.0", _noninteractive("1.0.0"))
    assert result == (False, False, "update.downgrade-not-allowed")


def test_noninteractive_same_version_blocked_without_force():
    result = _run("2.0.0", "2.0.0", _noninteractive("2.0.0"))
    assert result == (False, False, "update.version-already-installed")


def test_force_downgrade_allowed():
    result = _run("2.0.0", "1.0.0", _noninteractive("1.0.0", "--force"))
    assert result == (True, False, None)


def test_force_same_version_allowed():
    result = _run("2.0.0", "2.0.0", _noninteractive("2.0.0", "--force"))
    assert result == (True, False, None)


def test_interactive_downgrade_confirmed():
    assert _run("2.0.0", "1.0.0", [], answer=True) == (True, True, None)
    # The prompt text interpolates both versions
    assert _run.prompt_kwargs == {
        "existing_version": "2.0.0",
        "requested_version": "1.0.0",
    }


def test_interactive_downgrade_declined():
    result = _run("2.0.0", "1.0.0", [], answer=False)
    assert result == (False, True, "update.downgrade-not-allowed")


def test_interactive_same_version_does_not_prompt_downgrade():
    result = _run("2.0.0", "2.0.0", [], answer=True)
    assert result == (False, False, "update.version-already-installed")


def test_interactive_upgrade_does_not_prompt():
    assert _run("1.0.0", "2.0.0", []) == (True, False, None)
