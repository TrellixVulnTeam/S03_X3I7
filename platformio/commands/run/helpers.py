
from os import makedirs
from os.path import isdir, isfile, join

import click

from platformio import fs
from platformio.project.helpers import compute_project_checksum, get_project_dir


def handle_legacy_libdeps(project_dir, config):
    legacy_libdeps_dir = join(project_dir, ".piolibdeps")
    if not isdir(legacy_libdeps_dir) or legacy_libdeps_dir == config.get_optional_dir(
        "libdeps"
    ):
        return
    if not config.has_section("env"):
        config.add_section("env")
    lib_extra_dirs = config.get("env", "lib_extra_dirs", [])
    lib_extra_dirs.append(legacy_libdeps_dir)
    config.set("env", "lib_extra_dirs", lib_extra_dirs)
    click.secho(
        "DEPRECATED! A legacy library storage `{0}` has been found in a "
        "project. \nPlease declare project dependencies in `platformio.ini`"
        " file using `lib_deps` option and remove `{0}` folder."
        "\nMore details -> https://docs.OS-Q.com/page/projectconf/"
        "section_env_library.html#lib-deps".format(legacy_libdeps_dir),
        fg="yellow",
    )


def clean_build_dir(build_dir, config):
    # remove legacy ".pioenvs" folder
    legacy_build_dir = join(get_project_dir(), ".pioenvs")
    if isdir(legacy_build_dir) and legacy_build_dir != build_dir:
        fs.rmtree(legacy_build_dir)

    checksum_file = join(build_dir, "project.checksum")
    checksum = compute_project_checksum(config)

    if isdir(build_dir):
        # check project structure
        if isfile(checksum_file):
            with open(checksum_file) as fp:
                if fp.read() == checksum:
                    return
        fs.rmtree(build_dir)

    makedirs(build_dir)
    with open(checksum_file, "w") as fp:
        fp.write(checksum)