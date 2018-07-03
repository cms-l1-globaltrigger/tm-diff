XML Menu Diff
=============


## Basic usage

Compare the content of two XML trigger menus.

    $ tm-diff [-f|--format <format>] [-s|--skip <mode>] [--sort <key>]
              [-d|--dump] [-o <file>]
              <file1> <file2>

### Format

Use flag `-f|--format <format>` to select diff output format. Options are:

 * `unified` for unified diff format
 * `context` for contextual diff format
 * `html` for a complete diff in as HTML file
 * `report` to be copy-pasted into TWiki reports

Default format is `unified`.

**Example:**

    $ tm-diff ... -fhtml -o diff.html  # dumps diff as HTML table to file

### Skip

Use flag `-s|--skip <mode>` to ignore certain attributes. Options are

 * `module` to skip implementation details (attributes `uuid_firmware`, `n_modules`, `module_id`, `module_index`)
 * `comment` to skip comments (attribute `comment`)

**Example:**

    $ tm-diff ... -smodule -scomment  # ignores module_is/index and any comments

### Sort

Use flag `--sort <key>` to sort algorithms by attribute. Options are

 * `index` to sort by algorithm index
 * `name` to sort by algorithm name
 * `expression` to sort by algorithm expression

Default sort kay is `index`.

### Dump

Use flag `-d|--dump` to dump the raw text used to diff the menu contents. This
option will create two text files with the menu names at the current working location.

**Example:**

    $ tm-diff foo.xml bar.xml -d  # dumps raw text to foo.xml.txt bar.xml.txt

### Output

Use flag `-o <file>` to write the output to a file.

**Example:**

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
