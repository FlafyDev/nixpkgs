#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3Packages.pyyaml

import shutil
import json
import urllib.request
import tempfile
from sys import exit
import os
import subprocess
import re
import json
import argparse
import yaml
import json


NIXPKGS_ROOT = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'],
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')


def object_to_nix(obj):
    lines = re.sub(r'"(.*?)"(?= \=)', r'\1', json.dumps(obj,
                   indent=2, separators=(";", " = "))).splitlines()
    for i in range(len(lines)):
        line = lines[i]
        if line.strip().endswith('"') or line.strip().endswith(']') or line.strip().endswith('}'):
            lines[i] = line.rstrip() + ';'
    return '\n'.join(lines)[:-1]


# Return out paths
def nix_build(code):
    temp = tempfile.NamedTemporaryFile(mode='w')
    temp.write(code)
    temp.flush()
    os.fsync(temp.fileno())

    process = subprocess.Popen(
        ["nix", "build", "--impure", "--print-out-paths", "--no-link", "--expr",
            f"with import {NIXPKGS_ROOT} {{}}; callPackage {temp.name} {{}}"],
        stdout=subprocess.PIPE,
        text=None
    )

    process.wait()
    temp.close()
    return process.stdout.read().decode('utf-8').strip().splitlines()[0]


# Return errors
def nix_build_to_fail(code):
    temp = tempfile.NamedTemporaryFile(mode='w')
    temp.write(code)
    temp.flush()
    os.fsync(temp.fileno())

    process = subprocess.Popen(
        ["nix", "build", "--impure", "--keep-going", "--no-link", "--expr",
            f"with import {NIXPKGS_ROOT} {{}}; callPackage {temp.name} {{}}"],
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


def get_artifact_hashes(flutter_compact_version):
    flutter_compact_version = flutter_compact_version.replace('_', '')
    code = """
        {
          callPackage,
          flutter%s,
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
                    flutter = flutter%s;
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
    """.strip() % (flutter_compact_version, NIXPKGS_ROOT, flutter_compact_version)

    stderr = nix_build_to_fail(code)

    pattern = re.compile(
        r"/nix/store/.*-flutter-artifacts-(.+?)-(.+?).drv':\n\s+specified: .*\n\s+got:\s+(.+?)\n")
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
        stderr = nix_build_to_fail(code % (dartVersion))

        pattern = re.compile(r"got:\s+(.+?)\n")
        result_dict[platform] = pattern.findall(stderr)[0]

    return object_to_nix(result_dict)


def get_flutter_hash_and_src(flutter_version):
    code = """
        {fetchFromGitHub}: fetchFromGitHub {
          owner = "flutter";
          repo = "flutter";
          rev = "%s";
          hash = "";
        }
    """.strip() % (flutter_version)

    stderr = nix_build_to_fail(code)
    pattern = re.compile(r"got:\s+(.+?)\n")
    hash = pattern.findall(stderr)[0]

    code = """
        {fetchFromGitHub}: fetchFromGitHub {
          owner = "flutter";
          repo = "flutter";
          rev = "%s";
          hash = "%s";
        }
    """.strip() % (flutter_version, hash)

    return (hash, nix_build(code))


def write_default(nixpkgs_flutter_directory, flutter_version, engine_hash, dart_version, dart_hash, flutter_hash, artifact_hashes):
    with open(f"{nixpkgs_flutter_directory}/default.nix", "w") as f:
        f.write(f"""
{{
  version = "{flutter_version}";
  engineVersion = "{engine_hash}";
  dartVersion = "{dart_version}";
  dartHash = {dart_hash};
  flutterHash = "{flutter_hash}";
  artifactHashes = {artifact_hashes};
}}
    """.strip() + "\n")


def write_pubspec_lock_json(flutter_compact_version, nixpkgs_flutter_directory, flutter_src):
    flutter_compact_version = flutter_compact_version.replace('_', '')
    code = f"{{flutter{flutter_compact_version}}}: flutter{flutter_compact_version}.dart"

    dart_path = f"{nix_build(code)}/bin/dart"

    print(dart_path)
    print(' '.join([dart_path, 'pub', 'get', '-C',
          f"{flutter_src}/packages/flutter_tools", '-v']))

    process = subprocess.Popen(
        [dart_path, 'pub', 'get', '-C',
            f"{flutter_src}/packages/flutter_tools", '-v'],
        stderr=subprocess.PIPE,
        text=None
    )

    stderr = ""
    while True:
        line = process.stderr.readline()
        if not line:
            break
        stderr += line.decode('utf-8')

    process.wait()

    regex = r"FINE: Contents:\n.*Generated by pub(.|\n)*?ERR :"
    matches = re.search(regex, stderr)
    pubspec_lock_yaml = '\n'.join(
        [line[6:] for line in matches.group().strip().splitlines()[1:-1]])

    with open(f"{nixpkgs_flutter_directory}/pubspec.lock.json", "w") as f:
        f.write(json.dumps(yaml.safe_load(pubspec_lock_yaml), indent=2).strip() + "\n")


def update_all_packages():
    versions_directory = f"{NIXPKGS_ROOT}/pkgs/development/compilers/flutter/versions"
    versions = [directory for directory in os.listdir(versions_directory)]
    versions = sorted(versions, key=lambda x: int(x.split('_')[0]), reverse=True)

    new_content = [
        "flutterPackages = recurseIntoAttrs (callPackage ../development/compilers/flutter { });",
        "flutter = flutterPackages.stable;",
    ] + [f"flutter{version.replace('_', '')} = flutterPackages.v{version};" for version in versions]

    with open(f"{NIXPKGS_ROOT}/pkgs/top-level/all-packages.nix", 'r') as file:
        lines = file.read().splitlines(keepends=True)

    start = -1
    end = -1
    for i, line in enumerate(lines):
        if "flutterPackages = recurseIntoAttrs (callPackage ../development/compilers/flutter { });" in line:
            start = i
        if start != -1 and len(line.strip()) == 0:
            end = i
            break

    if start != -1 and end != -1:
        del lines[start:end]
        lines[start:start] = [f"  {l}\n" for l in new_content]

    with open(f"{NIXPKGS_ROOT}/pkgs/top-level/all-packages.nix", 'w') as file:
        file.write("".join(lines))


# Finds Flutter version, Dart version, and Engine hash.
# If the Flutter version is given, it uses that. Otherwise finds the latest stable Flutter version.
def find_versions(flutter_version=None):
    engine_hash = None
    dart_version = None

    releases = json.load(urllib.request.urlopen(
        "https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json"))

    if not flutter_version:
        stable_hash = releases['current_release']['stable']
        release = next(
            filter(lambda release: release['hash'] == stable_hash, releases['releases']))
        flutter_version = release['version']

    tags = subprocess.Popen(['git', 'ls-remote', '--tags', 'https://github.com/flutter/engine.git'],
                            stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')

    try:
        engine_hash = next(filter(lambda line: line.endswith(
            f'refs/tags/{flutter_version}'), tags.splitlines())).split('refs')[0].strip()
    except StopIteration:
        exit(
            f"Couldn't find Engine hash for Flutter version: {flutter_version}")

    try:
        dart_version = next(filter(
            lambda release: release['version'] == flutter_version, releases['releases']))['dart_sdk_version']
    except StopIteration:
        exit(
            f"Couldn't find Dart version for Flutter version: {flutter_version}")

    return (flutter_version, engine_hash, dart_version)


def main():
    parser = argparse.ArgumentParser(description='Update Flutter in Nixpkgs')
    parser.add_argument('--version', type=str, help='Specify Flutter version')
    parser.add_argument('--artifact-hashes', action='store_true',
                        help='Whether to get artifact hashes')
    args = parser.parse_args()

    (flutter_version, engine_hash, dart_version) = find_versions(args.version)

    flutter_compact_version = '_'.join(flutter_version.split('.')[:2])

    if args.artifact_hashes:
        print(get_artifact_hashes(flutter_compact_version))
        return

    print(f"Flutter version: {flutter_version} ({flutter_compact_version})")
    print(f"Engine hash: {engine_hash}")
    print(f"Dart version: {dart_version}")

    dart_hash = get_dart_hashes(dart_version).strip().replace('\n', '\n  ')
    (flutter_hash, flutter_src) = get_flutter_hash_and_src(flutter_version)

    nixpkgs_flutter_directory = f"{NIXPKGS_ROOT}/pkgs/development/compilers/flutter/versions/{flutter_compact_version}"

    shutil.rmtree(nixpkgs_flutter_directory, ignore_errors=True)
    os.makedirs(nixpkgs_flutter_directory)

    update_all_packages()

    write_default(nixpkgs_flutter_directory, flutter_version,
                  engine_hash, dart_version, dart_hash, flutter_hash, "{}")

    write_pubspec_lock_json(flutter_compact_version,
                            nixpkgs_flutter_directory, flutter_src)

    write_default(nixpkgs_flutter_directory, flutter_version, engine_hash, dart_version, dart_hash,
                  flutter_hash, get_artifact_hashes(flutter_compact_version).replace('\n', '\n  '))


if __name__ == "__main__":
    main()
