# Contributing to Kanagawa cursors

Thanks for helping. This port follows the
[Kanagawa community contributing guide](https://github.com/kanagawa-community/.github/blob/main/.github/CONTRIBUTING.md),
which explains conventional commits, the checks every pull request runs, and how
changes are reviewed. This page covers only what is specific to this port.

## Where to report what

- Problems with the cursors, such as wrong colors, poor
  contrast, or a missing variant, belong in this repository's
  [issue tracker](https://github.com/kanagawa-community/cursors/issues).
- Problems with the cursor shapes themselves belong with Vimix cursors. Start
  from the [project's page](https://github.com/vinceliuice/Vimix-cursors).
- Changes to the colors themselves belong in the
  [shared palette](https://github.com/kanagawa-community/.github/blob/main/docs/PALETTE.md),
  not in this port. Open an issue in the
  [.github repository](https://github.com/kanagawa-community/.github/issues)
  so every port stays in step.

## Colors

Take colors from the shared [palette](https://github.com/kanagawa-community/.github/blob/main/docs/PALETTE.md)
and follow the [style guide](https://github.com/kanagawa-community/.github/blob/main/docs/STYLE-GUIDE.md).
Do not sample colors from screenshots or add new ones. Every change must work in
Wave, Dragon, and Lotus.

To read the colors from a script, use the machine-readable
[palette.json](https://raw.githubusercontent.com/kanagawa-community/.github/main/palette.json).

## Working on this port

`upstream/` is a Git submodule of Vimix cursors, pinned to commit
[`9bc292f`](https://github.com/vinceliuice/Vimix-cursors/tree/9bc292f). The generator reads
its `src/` folder (SVGs, `config/`, `cursorList`). Clone with `--recurse-submodules`, or
run `git submodule update --init` in an existing clone. Users who only install the theme
do not need it. Do not change it. To update it, check out the new commit inside
`upstream/`, commit the new pointer, and regenerate.

`themes/` is generated. Do not edit it by hand. `scripts/generate.py` reads the shared
`palette.json` from a sibling checkout of the
[.github repository](https://github.com/kanagawa-community/.github) (or from a path given
as its first argument), swaps every color in the SVGs for a palette role, renders them
with `rsvg-convert` and packs them with `xcursorgen` (package `xorg-xcursorgen` on Arch,
`x11-apps` on Debian). It stops on any color it has no role for. After changing the
mapping, regenerate and commit the result:

```sh
python3 scripts/generate.py
```

The themes are binary and their bytes depend on the librsvg version, so unlike the other
ports there is no CI check that they are up to date. Regenerate before every commit.

To try a change, copy `themes/Kanagawa-Wave` to `~/.icons/` (Plasma does not list cursor
themes from `~/.local/share/icons`) and pick it in
your cursor settings. Some applications only load a new cursor theme after a restart.

The images in `assets/screenshots/` follow Vimix's own preview: the variant's cursors in
Vimix's grid order, on its `ui.bg` and `ui.fg`. Make one per variant, then
build the showcase and social preview with `scripts/finish-previews.sh` from the .github
repository. See the
[preview standard](https://github.com/kanagawa-community/.github/blob/main/docs/PREVIEWS.md).

## Pull requests

- Keep each pull request to one change, and include a screenshot of each variant
  it affects.
- Update the README when installation or usage changes.
