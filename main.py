from argparse import ArgumentParser
import subprocess
import os


def main():
    parser = ArgumentParser(
        prog="ffcli",
        description="simplified command line interface for ffmpeg",
    )

    subparsers = parser.add_subparsers()
    webm = subparsers.add_parser("webm")
    webm.add_argument("input_file")
    webm.add_argument("bitrate_type", choices=["crf", "vrf"])
    webm.add_argument("bitrate", help="2M for VRF, 28 for CRF")
    webm.add_argument(
        "-an", action="store_const", const="-an", default="", help="strip audio"
    )

    # parser.add_argument("output_format", default="webm", choices=["webm", "mp4"])

    cli = Wrapper()
    parser.parse_args(namespace=cli)
    print("DEBUG", vars(cli))

    cli.to_webm()


class Wrapper:
    input_file: str
    output_format: str
    bitrate_type: str
    bitrate: str

    def __init__(self):
        pass

    def to_webm(self):
        input = f"-i {self.input_file}"
        encoder = "-c:v libvpx-vp9"
        bitrate = f"-b:v {self.bitrate_type} {self.bitrate}"
        no_audio = "-an"
        no_output = "-f null /dev/null"  # linux
        no_output = "-f null NUL"  # windows

        output_file = os.path.splitext(self.input_file)[0] + ".webm"
        if output_file == self.input_file:
            if not confirm("Replace original file?"):
                abort("Aborted, no files written")
        elif os.path.exists(output_file):
            if not confirm(f"Override existing '{output_file}'?"):
                abort("Aborted, no files written")

        command = f"ffmpeg {input} {encoder} {bitrate} -pass 1 {no_audio} {no_output} && \
                    ffmpeg {input} {encoder} {bitrate} -pass 2 {no_audio} {output_file}"
        subprocess.check_call(command, shell=True)

    def to_mp4(self):
        raise Exception("not implemented")


def abort(prompt: str):
    print(prompt)
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


if __name__ == "__main__":
    main()
