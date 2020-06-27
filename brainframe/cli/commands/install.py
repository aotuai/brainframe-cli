from argparse import ArgumentParser
from pathlib import Path

import i18n

from brainframe.cli import (
    print_utils,
    docker_compose,
    defaults,
    env_vars,
    os_utils,
    dependencies,
)
from .utils import subcommand_parse_args


def install():
    args = _parse_args()

    if not os_utils.is_root():
        print_utils.fail_translate("install.user-not-root")

    # Print some introductory text
    if not args.noninteractive:
        print_utils.art()
        print_utils.translate("install.thanks")
        print("")
    if not os_utils.is_supported():
        print_utils.warning_translate("install.unsupported-os")
        print("")

    # Check all dependencies
    dependencies.curl.ensure(args.noninteractive, args.install_curl)
    dependencies.docker.ensure(args.noninteractive, args.install_docker)
    dependencies.docker_compose.ensure(
        args.noninteractive, args.install_docker_compose
    )

    if not os_utils.is_in_group("docker"):
        if args.noninteractive:
            add_to_group = args.add_to_docker_group
        else:
            add_to_group = print_utils.ask_yes_no(
                "install.ask-add-to-docker-group"
            )

        if add_to_group:
            os_utils.add_to_group("docker")

    # Set up the install path
    if args.noninteractive:
        install_path = args.install_path
    else:
        install_path = print_utils.ask_path(
            "install.ask-brainframe-install-path", defaults.INSTALL_PATH
        )
    install_path.mkdir(exist_ok=True, parents=True)

    # Set up the data path
    if args.noninteractive:
        data_path = args.data_path
    else:
        data_path = print_utils.ask_path(
            "install.ask-data-path", defaults.DATA_PATH
        )
    data_path.mkdir(exist_ok=True, parents=True)

    # Set up permissions with the 'brainframe' group
    print_utils.translate("install.create-group-justification")
    os_utils.create_group("brainframe", os_utils.BRAINFRAME_GROUP_ID)
    os_utils.give_brainframe_group_rw_access([data_path, install_path])

    # Ask the user if they want to be part of the "brainframe" group
    if args.noninteractive and args.add_to_group:
        os_utils.add_to_group("brainframe")
    elif not args.noninteractive:
        if print_utils.ask_yes_no("install.ask-add-to-group"):
            os_utils.add_to_group("brainframe")

    docker_compose.download(
        install_path / "docker-compose.yml", version=args.version
    )

    print_utils.translate("install.downloading-images")
    docker_compose.run(install_path, ["pull"])

    if not args.noninteractive and print_utils.ask_yes_no("install.ask-start"):
        docker_compose.run(install_path, ["up", "-d"])
    else:
        print_utils.translate("install.how-to-start")

    # Recommend to the user to add their custom paths to environment variables
    # so that future invocations of the program will know where to look.
    if (
        install_path != defaults.INSTALL_PATH
        or data_path != defaults.DATA_PATH
    ):
        print("")
        print_utils.translate("install.set-custom-directory-env-vars")
        print(
            f"\n"
            f'export {env_vars.INSTALL_PATH}="{install_path}"\n'
            f'export {env_vars.DATA_PATH}="{data_path}"\n'
        )

    print("")
    print_utils.translate("install.complete", print_utils.Color.GREEN)


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("install.description"),
        usage=i18n.t("install.usage"),
    )

    parser.add_argument(
        "--noninteractive",
        action="store_true",
        help=i18n.t("general.noninteractive-help"),
    )
    parser.add_argument(
        "--install-path",
        type=Path,
        default=defaults.INSTALL_PATH,
        help=i18n.t("install.install-path-help"),
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=defaults.DATA_PATH,
        help=i18n.t("install.data-path-help"),
    )
    parser.add_argument(
        "--install-docker",
        action="store_true",
        help=i18n.t("install.install-docker-help"),
    )
    parser.add_argument(
        "--install-docker-compose",
        action="store_true",
        help=i18n.t("install.install-docker-compose-help"),
    )
    parser.add_argument(
        "--install-curl",
        action="store_true",
        help=i18n.t("install.install-curl-help"),
    )
    parser.add_argument(
        "--add-to-group",
        action="store_true",
        help=i18n.t("install.add-to-group-help"),
    )
    parser.add_argument(
        "--add-to-docker-group",
        action="store_true",
        help=i18n.t("install.add-to-docker-group-help"),
    )
    parser.add_argument(
        "--version",
        type=str,
        default="latest",
        help=i18n.t("install.version-help"),
    )

    return subcommand_parse_args(parser)
