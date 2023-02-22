#!/usr/bin/env python3

import json
import pathlib
import shutil
import tempfile

import deepmerge
import hcl2
import jinja2
import yaml


def directory_copy(srcpath, dstpath, ignore=[]):
    """Copy the contents of the dir in 'srcpath' to the dir in 'dstpath'.

    Keyword arguments:
      srcpath[str]: path to source directory
      dstpath[str]: path to destination directory
      ignore[list]: files in srcpath to not ignore when copying
    """
    srcpath = pathlib.Path(srcpath)
    dstpath = pathlib.Path(dstpath)
    def ignorefunc(parent, items):
        return [
            item
            for item in items
            if (
                item in ignore
                or item == dstpath.name
                or parent == dstpath.name
            )
        ]
    shutil.copytree(srcpath, dstpath, ignore=ignorefunc, dirs_exist_ok=True)


def directory_remove(path, keep=[]):
    """Remove directory in 'path', but preserve any files in 'keep'.

    Keyword arguments:
      path[str]: path to directory
      keep[list]: files in directory to keep
    """
    path = pathlib.Path(path)
    if not path.is_dir():
        return

    temp = pathlib.Path(tempfile.TemporaryDirectory(dir=pathlib.Path().cwd()).name)
    for item in keep:
        itempath = path.joinpath(item)
        if itempath.exists():
            shutil.move(itempath, temp.joinpath(item))

    shutil.rmtree(path)

    for item in keep:
        itempath = temp.joinpath(item)
        if itempath.exists():
            shutil.move(itempath, path.joinpath(item))
    directory_remove(temp)


def json_read(paths):
    """Read JSON files in 'paths' and return their merged contents.

    Keyword arguments:
      paths[str/list]: path/s to JSON file/s, in ascending order of priority
    """
    assert(isinstance(paths, list))
    data = {}
    for path in paths:
        path = pathlib.Path(path)
        if not path.is_file():
            continue
        with open(path, "r") as f:
            data = deepmerge.always_merger.merge(data, json.load(f))
    return data


def json_write(data, path, indent=2):
    """Write 'data' to file in 'path' in JSON format.

    Keyword arguments:
      path[str]: destination file path
      data[any]: JSON-serializable data structure to write to file
      indent[int,optional]: number of spaces to indent JSON levels with
    """
    with open(pathlib.Path(path), "w") as f:
        json.dump(data, f, indent=indent)


def yaml_read(paths):
    """Read YAML files in 'paths' and return their merged contents.

    Keyword arguments:
      paths[str/list]: path/s to YAML file/s, in ascending order of priority
    """
    assert(isinstance(paths, list))
    data = {}
    for path in paths:
        path = pathlib.Path(path)
        if not path.is_file():
            continue
        with open(path, "r") as f:
            data = deepmerge.always_merger.merge(data, yaml.safe_load(f))
    return data


def yaml_write(data, path, indent=2, width=1000):
    """Write 'data' to file in 'path' in YAML format.

    Keyword arguments:
      path[str]: destination file path
      data[any]: YAML-serializable data structure to write to file
    """
    with open(pathlib.Path(path), "w") as f:
        yaml.dump(data, f, indent=indent, width=width)


def hcl2_read(paths):
    """Read HCL2 files in 'paths' and return their merged contents.

    Keyword arguments:
      paths[str/list]: path/s to HCL2 file/s, in ascending order of priority
    """
    assert(isinstance(paths, list))
    data = {}
    for path in paths:
        path = pathlib.Path(path)
        if not path.is_file():
            continue
        with open(path, "r") as f:
            data = deepmerge.always_merger.merge(data, hcl2.load(f))
    return data


def jinja2_render(paths, data):
    """Overwrite files in 'paths' with their Jinja2 render.

    Keyword arguments:
      paths[str/list]: path/s to text file/s
      data[dict]: variables to render files with
    """
    assert(isinstance(paths, list))
    for path in paths:
        path = pathlib.Path(path)
        if not path.is_file():
            continue
        with open(path, "r") as fin:
            template = jinja2.Template(fin.read())
        rendered = template.render(data)
        with open(path, "w") as fout:
            fout.write(rendered)