import tempfile
import asyncio
import os
import subprocess
import re
import json

NIXPKGS_ROOT = os.getcwd();

def object_to_nix(obj):
    lines = json.dumps(obj, indent=2, separators=(";", " = ")).splitlines();
    for i in range(len(lines)):
        line = lines[i]
        if line.strip().endswith('"') or line.strip().endswith(']') or line.strip().endswith('}'):
            lines[i] = line.rstrip() + ';'
    return '\n'.join(lines)[:-1]


def run_nix_code(code):
    temp = tempfile.NamedTemporaryFile(mode='w')
    temp.write(code)
    temp.flush()
    os.fsync(temp.fileno())

    process = subprocess.Popen(
        ["nix", "build", "--impure", "--keep-going", "--expr", f"with import ./. {{}}; callPackage {temp.name} {{}}"],
        stderr=subprocess.PIPE,
        text=None
    )

    stderr = ""
    while True:
        line = process.stderr.readline()
        if not line:
            break
        stderr += line.decode('utf-8')
        print(line.decode('utf-8').strip())

    process.wait()
    temp.close()
    return stderr


def get_artifect_hashes():
    code = """
        {
          callPackage,
          flutter,
          lib,
          symlinkJoin,
        }: let
          flutterPlatforms = [
            "android"
            "ios"
            "web"
            "linux"
            "windows"
            "macos"
            "fuchsia"
            "universal"
          ];
          systemPlatforms = [
            "x86_64-linux"
            "aarch64-linux"
            "x86_64-darwin"
          ];

          derivations =
            lib.foldl' (
              acc: flutterPlatform:
                acc
                ++ (map (systemPlatform:
                  callPackage "%s/pkgs/development/compilers/flutter/artifacts/fetch-artifacts.nix" {
                    inherit flutter;
                    inherit flutterPlatform;
                    inherit systemPlatform;
                    hash = "";
                  })
                systemPlatforms)
            ) []
            flutterPlatforms;
        in
          symlinkJoin {
            name = "evaluate-derivations";
            paths = derivations;
          }
    """.strip() % (NIXPKGS_ROOT);

    stderr = run_nix_code(code)

    pattern = re.compile(r"/nix/store/.*-flutter-artifacts-(.+?)-(.+?).drv':\n\s+specified: .*\n\s+got:\s+(.+?)\n")
    matches = pattern.findall(stderr)
    result_dict = {}

    for match in matches:
        flutter_platform, architecture,  got = match
        result_dict.setdefault(flutter_platform, {})[architecture] = got

    def sort_dict_recursive(d):
        return {k: sort_dict_recursive(v) if isinstance(v, dict) else v for k, v in sorted(d.items())}
    result_dict = sort_dict_recursive(result_dict)

    return object_to_nix(result_dict)


def get_dart_hashes(dartVersion):
    code = {
        "x86_64-linux": """
            { fetchzip }: fetchzip {
              url = "https://storage.googleapis.com/dart-archive/channels/stable/release/%s/sdk/dartsdk-linux-x64-release.zip";
              sha256 = "";
            }
            """.strip(),
        "aarch64-linux": """
            { fetchzip }: fetchzip {
              url = "https://storage.googleapis.com/dart-archive/channels/stable/release/%s/sdk/dartsdk-linux-arm64-release.zip";
              sha256 = "";
            }
        """.strip(),
        "x86_64-darwin": """
            { fetchzip }: fetchzip {
              url = "https://storage.googleapis.com/dart-archive/channels/stable/release/%s/sdk/dartsdk-macos-x64-release.zip";
              sha256 = "";
            }
        """.strip(),
        "aarch64-darwin": """
            { fetchzip }: fetchzip {
              url = "https://storage.googleapis.com/dart-archive/channels/stable/release/%s/sdk/dartsdk-macos-arm64-release.zip";
              sha256 = "";
            }
        """.strip(),
    }
    result_dict = {}
    for (platform, code) in code.items():
        stderr = run_nix_code(code % (dartVersion))

        pattern = re.compile(r"got:\s+(.+?)\n")
        result_dict[platform] = pattern.findall(stderr)[0]

    return object_to_nix(result_dict)


def get_flutter_hash(flutter_version):
    code = """
        {fetchFromGitHub}: fetchFromGitHub {
          owner = "flutter";
          repo = "flutter";
          rev = "%s";
          hash = "";
        }
    """.strip() % (flutter_version);

    stderr = run_nix_code(code)

    pattern = re.compile(r"got:\s+(.+?)\n")
    return pattern.findall(stderr)[0]


def main():
    flutter_version = input("Flutter version(e.g. 3.13.8): ")
    engine_version = input("Engine commit(e.g. 767d8c75e898091b925519803830fc2721658d07): ")
    dart_version = input("Dart version(e.g. 3.1.4): ")

    if (input("Get artifect hashes? (y/n): ").lower() == "y"):
        print(get_artifect_hashes())

    dart_hash = get_dart_hashes(dart_version).strip().replace('\n', '\n  ')
    flutter_hash = get_flutter_hash(flutter_version)

    print(f"""
mkFlutter {{
  version = "{flutter_version}";
  engineVersion = "{engine_version}";
  dartVersion = "{dart_version}";
  dartHash = {dart_hash};
  flutterHash = "{flutter_hash}";
  patches = flutter3Patches;
  pubspecLockFile = ./lockfiles/stable/pubspec.lock;
  vendorHash = "";
  depsListFile = ./lockfiles/stable/deps.json;
}};
    """.strip());

if __name__ == "__main__":
    main()
