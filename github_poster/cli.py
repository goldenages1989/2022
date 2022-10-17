#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# some code from https://github.com/flopp/GpxTrackPoster

import argparse
import os
import sys

from github_poster.circluar_drawer import CircularDrawer
from github_poster.config import TYPE_INFO_DICT
from github_poster.drawer import Drawer
from github_poster.err import DepNotInstalledError
from github_poster.loader import LOADER_DICT
from github_poster.poster import Poster
from github_poster.utils import parse_years

OUT_FOLDER = os.path.join(os.getcwd(), "OUT_FOLDER")


def run():
    """Handle command line arguments and call other modules as needed."""
    p = Poster()
    args_parser = argparse.ArgumentParser()
    subparser = args_parser.add_subparsers()

    # temp list to remove the summary type
    temp_list = list(LOADER_DICT.values()).copy()
    temp_list.remove(LOADER_DICT.get("summary"))
    temp_list.remove(LOADER_DICT.get("multiple"))

    for type_, l in LOADER_DICT.items():  # l -> loader class
        l._type = type_
        parser = subparser.add_parser(name=type_)
        parser.set_defaults(type=type_, loader=l)
        optional = True
        if type_ in ["summary", "multiple"]:
            l.parser_loader_list = list(temp_list)
            optional = False
        l.add_arguments(parser, optional)

    args = args_parser.parse_args()
    # without title
    no_title_types = ("issue", "multiple", "json")

    p.colors = {
        "background": args.background_color,
        "track": args.track_color
        or args.loader.track_color,  # some type has default color
        "special": args.special_color1,
        "special2": args.special_color2 or args.special_color,
        "text": args.text_color,
    }

    # if special color (Stand with Ukraine) change the color
    if args.stand_with_ukraine:
        p.colors["track"] = "#025DB8"
        p.colors["special"] = "#FFD100"
        p.colors["special2"] = "#FFD100"

    # set animate
    p.set_with_animation(args.with_animation)
    p.set_animation_time(args.animation_time)
    from_year, to_year = parse_years(args.year)
    args_dict = dict(args._get_kwargs())
    loader = LOADER_DICT.get(args.type, "duolingo")(
        from_year, to_year, args.type, **args_dict
    )
    type_list = [args.type]
    # for multiple types or year summary
    if args.type in ["multiple", "summary"]:
        p.units = args.loader.unit
        types_list = args_dict.get("types").split(",")
        # trim drop the spaces
        type_list = [t.replace(" ", "") for t in types_list]
        if args.with_skyline or args.is_circular:
            raise Exception("Skyline or Circular does not support for multiple types")
        if args.type == "multiple":
            assert len(types_list) <= 3
        for t in type_list:
            if t not in LOADER_DICT:
                raise Exception(f"{t} must in support loader types")
            loader.set_loader_list(
                LOADER_DICT.get(t)(from_year, to_year, t, **args_dict)
            )
            p.loader_list = loader.loader_list

    if args.type != "summary":
        tracks, years = loader.get_all_track_data()
        p.units = args.loader.unit
        p.set_tracks(tracks, years, type_list)
    else:
        p.units = args.loader.unit
        p.set_tracks({}, [to_year], type_list)

    # set title
    # we don't know issue content so use name
    p.title = (
        f"{args.me } {str(to_year) + ' ' if args.type=='summary' else ''}"
        + TYPE_INFO_DICT.get(args.type, args.type)
        if args.type not in no_title_types and args.without_type_name
        else args.me
    )

    p.special_number = {
        "special_number1": loader.special_number1,
        "special_number2": loader.special_number2,
    }
    if args.special_number1:
        p.special_number["special_number1"] = args.special_number1
    if args.special_number2:
        p.special_number["special_number2"] = args.special_number2
    # the length of this poster
    poster_length = len(p.years) if args.type != "summary" else len(loader.loader_list)
    p.height = 35 + poster_length * 43
    if not os.path.exists(OUT_FOLDER):
        os.mkdir(OUT_FOLDER)
    # support different issues, maybe better way
    file_name = str(args.type)

    # make different drawer
    is_circular = args.is_circular
    d = CircularDrawer if is_circular else Drawer
    if args.type == "issue":
        issue_number = args_dict.get("issue_number", "1")
        repo_name = args_dict.get("repo_name", "").replace("/", "_")
        file_name = f"issue_{repo_name}_{issue_number}"
    if args.type == "summary":
        file_name = f"summary_{to_year}"
        p.is_summary = True
    if is_circular:
        file_name = f"{file_name}_circular"

        # circular type is 120*120 square
        p.height = 120
        p.width = 120

    file_name = f"{file_name}.svg"

    # for summary we have different logic #TODO refactor
    p.draw(d(p), os.path.join(OUT_FOLDER, file_name))

    # generate skyline
    if args.with_skyline:
        try:
            from github_poster.skyline import Skyline
        except ImportError:
            raise DepNotInstalledError(
                "Skyline dependencies are not installed, "
                "please use `pip3 install -U 'github_poster[skyline]'` to install."
            )

        if args.skyline_year:
            year = args.skyline_year
        else:
            year = years[-1]
        # filter data
        number_by_date_dict = {k: v for k, v in tracks.items() if k[:4] == str(year)}
        skyline_name = ""
        if args.skyline_with_name:
            skyline_name = args.me
        s = Skyline(
            os.path.join(OUT_FOLDER, f"{year}_{str(args.type)}" + ".stl"),
            year,
            args.type,
            number_by_date_dict,
            skyline_name,
        )
        s.type_info_dict = TYPE_INFO_DICT
        s.make_skyline()


def main():
    try:
        run()
    except DepNotInstalledError as e:
        print(e, file=sys.stderr)


if __name__ == "__main__":
    main()
