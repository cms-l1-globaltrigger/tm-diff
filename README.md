XML Diff
========


## Basic usage

Compare the content of two XML trigger menus using unified diff.

    $ tm-diff [-d|--dump] [--skip-impl] <file1> <file2>

Use flag `-d|--dump` to dump the raw text used to diff the menu contents. This
option will create two text files with the menu names at the current working location.

Use flag `--skip-impl` to ignore implementation details `module_id` and `module_index`.


## Dependencies

 * `tmTable`

**Note:** make sure to set `UTM_ROOT` before executing.


## Setup

    $ . /path/to/utm-0.6.x/setup.sh  # source UTM environment

    $ git clone https://gitlab.cern.ch/.../tm-diff.git
    $ cd tm-diff
    $ . setup.sh
    $
