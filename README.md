XML Menu Diff
=============


## Basic usage

Compare the content of two XML trigger menus.

    $ tm-diff [-f|--format <format>] [-s|--skip <mode>] [-d|--dump] [-o <file>] <file1> <file2>

Use flag `-f|--format <format>` to select diff output format. Options are:

 * `unified` for unified diff format
 * `context` for contextual diff format
 * `html` for a complete diff in as HTML file
 * `report` to be copy-pasted into TWiki reports

Default format is `unified`.

**Example**

    $ tm-diff ... -fhtml -o diff.html  # dumps diff as HTML table to file

Use flag `--skip <mode>` to ignore certain attributes. Options are

 * `module` to skip implementation details (attributes `firmware_uuid`, `n_modules`, `module_id` and `module_index`)
 * `comment` to skip comments (attribute `comment`)

**Example**

    $ tm-diff ... -smodule -scomment  # ignores module_is/index and any comments

Use flag `-d|--dump` to dump the raw text used to diff the menu contents. This
option will create two text files with the menu names at the current working location.

**Example**

    $ tm-diff foo.xml bar.xml -d  # dumps raw text to foo.xml.txt bar.xml.txt

Use flag `-o <file>` to write the output to a file.

**Example**

    $ tm-diff foo.xml bar.xml -o diff.txt  # write output to file

This is equivalent to:

    $ tm-diff foo.xml bar.xml > diff.txt  # pipe stdout to file


## Dependencies

 * `tmTable`

**Note:** make sure to set `UTM_ROOT` before executing.


## Setup

    $ . /path/to/utm-0.6.x/setup.sh  # source UTM environment

    $ git clone https://gitlab.cern.ch/.../tm-diff.git
    $ cd tm-diff
    $ . setup.sh
    $
