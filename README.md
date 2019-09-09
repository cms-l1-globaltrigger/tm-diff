XML Menu Diff
=============


## Basic usage

Compare the content of two XML trigger menus.

```bash
tm-diff [-f|--format <format>] [-s|--skip <mode>] [--sort <key>]
        [-d|--dump] [-o <file>]
        <file1> <file2>
```

### Format

Use flag `-f|--format <format>` to select diff output format. Options are:

 * `unified` for unified diff format
 * `context` for contextual diff format
 * `html` for a complete diff in as HTML file
 * `report` to be copy-pasted into TWiki reports

Default format is `unified`.

**Example:**

```bash
tm-diff ... -fhtml -o diff.html  # dumps diff as HTML table to file
```

### Skip

Use flag `-s|--skip <mode>` to ignore certain attributes. Options are

 * `module` to skip implementation details (attributes `uuid_firmware`, `n_modules`, `module_id`, `module_index`)
 * `comment` to skip comments (attribute `comment`)

**Example:**

```bash
tm-diff ... -smodule -scomment  # ignores module_is/index and any comments
```

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

```bash
tm-diff foo.xml bar.xml -d  # dumps raw text to foo.xml.txt bar.xml.txt
```

### Output

Use flag `-o <file>` to write the output to a file.

**Example:**

```bash
tm-diff foo.xml bar.xml -o diff.txt  # write output to file
```

This is equivalent to:

```bash
tm-diff foo.xml bar.xml > diff.txt  # pipe stdout to file
```

## Dependencies

Install following l1t-utm wheel or build l1t-utm python bindings.

 * `tmTable>=0.7.3`


## Install

Install using pip

```bash
pip install https://github.com/cms-l1-globaltrigger/tm-diff/archive/master.zip#egg=tm-diff-0.6.0
```

Install from local source

```bash
git clone https://gitlab.cern.ch/cms-l1-globaltrigger/tm-diff.git
cd tm-diff
python setup.py test
python setup.py install
```
