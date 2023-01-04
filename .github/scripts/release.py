import subprocess

from concurrentbuffer import __version__


def create_new_release():
    subprocess.run(
        ["gh", "release", "create", "--notes", "''", "v" + __version__],
        check=True,
    )


if __name__ == "__main__":
    create_new_release()
