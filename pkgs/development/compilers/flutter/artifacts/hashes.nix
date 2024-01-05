# NOTICE: When updating these hashes, make sure that no additional platforms
# have been added to the `flutter precache` CLI. If any have, they may be
# included in every derivation, unless they are also added to the platform list
# in fetch-artifacts.nix.
#
# The known arguments are as follows:
# $ flutter precache --help --verbose
# Usage: flutter precache [arguments]
# -h, --help                              Print this usage information.
# -a, --all-platforms                     Precache artifacts for all host platforms.
# -f, --force                             Force re-downloading of artifacts.
#     --[no-]android                      Precache artifacts for Android development.
#     --[no-]android_gen_snapshot         Precache gen_snapshot for Android development.
#     --[no-]android_maven                Precache Gradle dependencies for Android development.
#     --[no-]android_internal_build       Precache dependencies for internal Android development.
#     --[no-]ios                          Precache artifacts for iOS development.
#     --[no-]web                          Precache artifacts for web development.
#     --[no-]linux                        Precache artifacts for Linux desktop development.
#     --[no-]windows                      Precache artifacts for Windows desktop development.
#     --[no-]macos                        Precache artifacts for macOS desktop development.
#     --[no-]fuchsia                      Precache artifacts for Fuchsia development.
#     --[no-]universal                    Precache artifacts required for any development platform.
#                                         (defaults to on)
#     --[no-]flutter_runner               Precache the flutter runner artifacts.
#     --[no-]use-unsigned-mac-binaries    Precache the unsigned macOS binaries when available.

# Schema:
# ${flutterVersion}.${targetPlatform}.${hostPlatform}
#
# aarch64-darwin as a host is not yet supported.
# https://github.com/flutter/flutter/issues/60118
{
  "3.16.5" = {
    "android" = {
      "aarch64-linux" = "sha256-kg5nsPlgVlaVO9C7Ve38MUyTyWSmCanWSE1Y+yyJtqE=";
      "x86_64-darwin" = "sha256-kg5nsPlgVlaVO9C7Ve38MUyTyWSmCanWSE1Y+yyJtqE=";
      "x86_64-linux" = "sha256-kg5nsPlgVlaVO9C7Ve38MUyTyWSmCanWSE1Y+yyJtqE=";
    };
    "fuchsia" = {
      "aarch64-linux" = "sha256-eu0BERdz53CkSexbpu3KA7O6Q4g0s9SGD3t1Snsk3Fk=";
      "x86_64-darwin" = "sha256-eu0BERdz53CkSexbpu3KA7O6Q4g0s9SGD3t1Snsk3Fk=";
      "x86_64-linux" = "sha256-eu0BERdz53CkSexbpu3KA7O6Q4g0s9SGD3t1Snsk3Fk=";
    };
    "ios" = {
      "aarch64-linux" = "sha256-wg2Ri7FAhv3wrzMuYTDzkLO5nbIPy0H9tI8TI9z6Fhw=";
      "x86_64-darwin" = "sha256-wg2Ri7FAhv3wrzMuYTDzkLO5nbIPy0H9tI8TI9z6Fhw=";
      "x86_64-linux" = "sha256-wg2Ri7FAhv3wrzMuYTDzkLO5nbIPy0H9tI8TI9z6Fhw=";
    };
    "linux" = {
      "aarch64-linux" = "sha256-QsTTNye/pjqK8jNSe20t6xY//EeUYxnGguWjaCaUm9A=";
      "x86_64-darwin" = "sha256-osmqqm9y261qTQEg4ponQlqub5PtEOaJ1npaL0ZDEog=";
      "x86_64-linux" = "sha256-osmqqm9y261qTQEg4ponQlqub5PtEOaJ1npaL0ZDEog=";
    };
    "macos" = {
      "aarch64-linux" = "sha256-54Fvmq7Ee8aWXlh0e1ukaxMwMMrEESmsra2b8JOQDec=";
      "x86_64-darwin" = "sha256-54Fvmq7Ee8aWXlh0e1ukaxMwMMrEESmsra2b8JOQDec=";
      "x86_64-linux" = "sha256-54Fvmq7Ee8aWXlh0e1ukaxMwMMrEESmsra2b8JOQDec=";
    };
    "universal" = {
      "aarch64-linux" = "sha256-yHRVZelR/y30DvAKQz8/IHbiGsvq1tfzsNbx2VMn2YU=";
      "x86_64-darwin" = "sha256-w+nQUeit0CJejQKPY7/ZwpKWvb2owewH+FcTy+wdGY8=";
      "x86_64-linux" = "sha256-w+nQUeit0CJejQKPY7/ZwpKWvb2owewH+FcTy+wdGY8=";
    };
    "web" = {
      "aarch64-linux" = "sha256-TOmro8ugInKec/mRhpAs8FYonmHNKFZmX/xZYFyslI0=";
      "x86_64-darwin" = "sha256-TOmro8ugInKec/mRhpAs8FYonmHNKFZmX/xZYFyslI0=";
      "x86_64-linux" = "sha256-TOmro8ugInKec/mRhpAs8FYonmHNKFZmX/xZYFyslI0=";
    };
    "windows" = {
      "aarch64-linux" = "sha256-qPN3TQnKOBk+y4Z+3v4Zrto6s6wj75WYbsoZ4C3KOb0=";
      "x86_64-darwin" = "sha256-qPN3TQnKOBk+y4Z+3v4Zrto6s6wj75WYbsoZ4C3KOb0=";
      "x86_64-linux" = "sha256-qPN3TQnKOBk+y4Z+3v4Zrto6s6wj75WYbsoZ4C3KOb0=";
    };
  };
}
