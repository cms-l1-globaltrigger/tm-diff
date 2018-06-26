XML Menu Diff
=============


## Basic usage

Compare the content of two XML trigger menus.

    $ tm-diff [-f|--format <fmt>] [-s|--skip <mode>] [-d|--dump] <file1> <file2>

Use flag `-f|--format` to select diff output format. Options are `unified`,
 `context` and `report` (to be copy-pasted into TWiki reports). Default is `unified`.

    $ tm-diff ... -freport  # prints output in TWiki report format

Use flag `--skip <module|comment>` to ignore module specific implementation
details (attributes `module_id` and `module_index`) or comments (attribute `comment`).

    $ tm-diff ... -smodule -scomment  # ignores module_is/index and any comments

Use flag `-d|--dump` to dump the raw text used to diff the menu contents. This
option will create two text files with the menu names at the current working location.

    $ tm-diff foo.xml bar.xml -d  # dumps raw text to foo.xml.txt bar.xml.txt


## Dependencies

 * `tmTable`

**Note:** make sure to set `UTM_ROOT` before executing.


## Setup

    $ . /path/to/utm-0.6.x/setup.sh  # source UTM environment

    $ git clone https://gitlab.cern.ch/.../tm-diff.git
    $ cd tm-diff
    $ . setup.sh
    $
