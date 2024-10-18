from argparse import ArgumentParser
from typing import Any
import subprocess
import os


def main():
    cli = Wrapper()
    argument_parser = ArgumentParser(
        prog="ffcli",
        description="simplified command line interface for ffmpeg",
    )

    subparsers = argument_parser.add_subparsers()
    webm = subparsers.add_parser("webm")
    webm.set_defaults(run=cli.to_webm)
    webm.add_argument("bitrate_type", choices=["crf", "vrf"])
    webm.add_argument("bitrate", help="2M for VRF, 15-35 for CRF")
    webm.add_argument(
        "-an",
        action="store_const",
        const="-an",
        default="",
        help="strip audio",
    )
    webm.add_argument(
        "--height",
        default="",
        help="set output height",
    )
    webm.add_argument("input_file")

    argument_parser.parse_args(namespace=cli)
    cli.run()


class Wrapper:
    run: Any  # function invoked by ArgumentParser
    input_file: str
    output_format: str
    bitrate_type: str
    bitrate: str
    an: str
    height: str

    def __init__(self):
        pass

    def to_webm(self):
        input = f"-i {self.input_file}"
        output_file = os.path.splitext(self.input_file)[0] + ".webm"

        if output_file == self.input_file:
            if not confirm("Replace original file?"):
                abort("Aborted, no files written")
        elif os.path.exists(output_file):
            if not confirm(f"Override existing '{output_file}'?"):
                abort("Aborted, no files written")

        audio = self.an if self.an else "-c:a libopus"
        encoder = "-c:v libvpx-vp9"
        no_output = "-f null /dev/null"  # linux
        no_output = "-f null NUL"  # windows

        scale = f"-vf scale=-1:{self.height}" if self.height else ""

        if self.bitrate_type == "vrf":
            bitrate = f"-b:v {self.bitrate}"
            command = (  # Two-pass average bitrate
                f"ffmpeg {input} {encoder} {scale} {bitrate} -pass 1 -an {no_output} && "
                f"ffmpeg -y {input} {encoder} {scale} {bitrate} -pass 2 {audio} {output_file}"
            )
            log_command(command)
        elif self.bitrate_type == "crf":
            bitrate = f"-crf {self.bitrate} -b:v 0"
            command = (  # Constant Quality
                f"ffmpeg {input} {encoder} {bitrate} {audio} {output_file}"
            )
            log_command(command)
        else:
            raise Exception("bitrate_type unknown")

        subprocess.check_call(command, shell=True)

    def to_mp4(self):
        raise Exception("not implemented")


def abort(text: str):
    print(text)
    exit()


def confirm(prompt: str):
    RED = "\033[31m"
    RESET = "\033[0m"
    prompt = f"{RED}{prompt} (y/n):{RESET} "
    while True:
        user_input = input(prompt).lower()
        if user_input not in ["y", "n"]:
            print(prompt)
        else:
            return user_input == "y"


def log_command(text: str):
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    text = f"executing {YELLOW}{text}{RESET}"
    print(text)


if __name__ == "__main__":
    main()
