from argparse import ArgumentParser
from pathlib import Path

import i18n
from brainframe.cli import (
    config,
    dependencies,
    docker_compose,
    os_utils,
    print_utils,
)

from .utils import command, subcommand_parse_args


@command("install")
def install():
    args = _parse_args()

    if not os_utils.is_root():
        print_utils.fail_translate("general.user-not-root")

    # Print some introductory text
    if not args.noninteractive:
        print_utils.art()
        print_utils.translate("install.thanks")
        print()
    if not os_utils.is_supported():
        print_utils.warning_translate("install.unsupported-os")
        print()

    # Check all dependencies
    dependencies.curl.ensure(args.noninteractive, args.install_curl)
    dependencies.docker.ensure(args.noninteractive, args.install_docker)

    _, _, download_version = docker_compose.check_download_version()
    print_utils.translate("install.install-version", version=download_version)

    if not os_utils.added_to_group("docker"):
        if args.noninteractive:
            add_to_group = args.add_to_docker_group
        else:
            add_to_group = print_utils.ask_yes_no(
                "install.ask-add-to-docker-group"
            )

        if add_to_group:
            os_utils.add_to_group("docker")

    use_default_paths = False
    if not args.noninteractive:
        # Ask the user if they want to specify special paths for installation
        print_utils.translate(
            "install.default-paths",
            default_install_path=config.install_path.default,
            default_data_path=config.data_path.default,
        )
        use_default_paths = print_utils.ask_yes_no(
            "install.ask-use-default-paths",
        )

    # Set up the install path
    if args.noninteractive:
        install_path = args.install_path
    elif use_default_paths:
        install_path = config.install_path.default
    else:
        install_path = print_utils.ask_path(
            "install.ask-brainframe-install-path", config.install_path.default,
        )
    install_path.mkdir(exist_ok=True, parents=True)

    # Set up the data path
    if args.noninteractive:
        data_path = args.data_path
    elif use_default_paths:
        data_path = config.data_path.default
    else:
        data_path = print_utils.ask_path(
            "install.ask-data-path", config.data_path.default
        )
    data_path.mkdir(exist_ok=True, parents=True)

    # Set up permissions with the 'brainframe' group
    print_utils.translate("install.create-group-justification")
    os_utils.create_group("brainframe", os_utils.BRAINFRAME_GROUP_ID)
    os_utils.give_brainframe_group_rw_access([data_path, install_path])

    # Optionally add the user to the "brainframe" group
    if not os_utils.added_to_group("brainframe"):
        if args.noninteractive:
            add_to_group = args.add_to_group
        else:
            add_to_group = print_utils.ask_yes_no("install.ask-add-to-group")

        if add_to_group:
            os_utils.add_to_group("brainframe")

    docker_compose.download(
        install_path / "docker-compose.yml", version=args.version
    )

    print_utils.translate("install.downloading-images")
    docker_compose.run(install_path, ["pull"])

    print()
    print_utils.translate("install.complete", print_utils.Color.GREEN)

    if not args.noninteractive and print_utils.ask_yes_no("install.ask-start"):
        docker_compose.run(install_path, ["up", "-d"])
        print()
        print_utils.translate("install.running", print_utils.Color.GREEN)
    else:
        print_utils.translate("install.how-to-start")

    # Recommend to the user to add their custom paths to environment variables
    # so that future invocations of the program will know where to look.
    if (
        install_path != config.install_path.default
        or data_path != config.data_path.default
    ):
        print()
        print_utils.translate("install.set-custom-directory-env-vars")
        print(
            f"\n"
            f'export {config.install_path.name}="{install_path}"\n'
            f'export {config.data_path.name}="{data_path}"\n'
        )


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
        default=config.install_path.default,
        help=i18n.t("install.install-path-help"),
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=config.data_path.default,
        help=i18n.t("install.data-path-help"),
    )
    parser.add_argument(
        "--install-docker",
        action="store_true",
        help=i18n.t("install.install-docker-help"),
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
