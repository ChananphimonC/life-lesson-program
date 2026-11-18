"""Library manager: `python -m life_lesson.library <command>`.

  list        show episodes / Shorts (filter by kind, state, playlist)
  show        details + file locations of one episode
  export      copy the MP4 to the export folder (download for upload)
  delete      remove an episode and its files (asks for --yes)
  thumbnail   edit the cover: title / tag / subline / backdrop frame or image
  description rebuild title + description (chapters, facts, credits, channel link)
  short       cut a Short from a finished episode (30-55 s + "watch full" card)
  export-legacy  copy into the owner's EPxx / Shorts library folders
  playlist    create | list | show | add | remove | rename | delete  (folders too)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from life_lesson.config import get_settings
from life_lesson.db import repository as repo
from life_lesson.errors import PipelineError
from life_lesson.library import service


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="life_lesson.library", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list"); ls.add_argument("--kind", choices=["episode", "short"]); ls.add_argument("--state"); ls.add_argument("--playlist")
    sh = sub.add_parser("show"); sh.add_argument("ref")
    ex = sub.add_parser("export"); ex.add_argument("ref"); ex.add_argument("--to", type=Path); ex.add_argument("--name")
    de = sub.add_parser("delete"); de.add_argument("ref"); de.add_argument("--yes", action="store_true")
    de.add_argument("--keep-files", action="store_true"); de.add_argument("--with-shorts", action="store_true")
    th = sub.add_parser("thumbnail"); th.add_argument("ref"); th.add_argument("--title"); th.add_argument("--tag"); th.add_argument("--subline")
    th.add_argument("--frame-at", type=float); th.add_argument("--image", type=Path)
    lg = sub.add_parser("export-legacy", help="put an episode/Short into the owner's existing library folders")
    lg.add_argument("ref"); lg.add_argument("--videos-dir", type=Path, help="cartoon_storyboard/output/videos")
    lg.add_argument("--shorts-dir", type=Path, help="experiments/shorts/output")
    ds = sub.add_parser("description"); ds.add_argument("ref"); ds.add_argument("--full-url")
    st = sub.add_parser("short"); st.add_argument("ref"); st.add_argument("--full-url"); st.add_argument("--nth", type=int, default=1, help="1 = best window, 2 = second best ...")
    st.add_argument("--layout", choices=["fit", "tall"], default="fit", help="fit = whole frame over blur; tall = crop centre to fill the screen")
    st.add_argument("--min", type=float, default=30); st.add_argument("--max", type=float, default=55)

    pl = sub.add_parser("playlist"); psub = pl.add_subparsers(dest="pcmd", required=True)
    c = psub.add_parser("create"); c.add_argument("name"); c.add_argument("--folder", action="store_true")
    psub.add_parser("list")
    s = psub.add_parser("show"); s.add_argument("name")
    for name in ("add", "remove"):
        x = psub.add_parser(name); x.add_argument("name"); x.add_argument("refs", nargs="+")
    r = psub.add_parser("rename"); r.add_argument("name"); r.add_argument("new_name")
    d = psub.add_parser("delete"); d.add_argument("name"); d.add_argument("--yes", action="store_true")
    return p


def _line(row) -> str:
    return f"{row['id'][:8]}  {row['kind']:<7} {(row['format'] or '-'):<8} {row['state']:<13} {row['title'] or '(untitled)'}"


def _playlist(conn, args) -> int:
    pc = args.pcmd
    if pc == "create":
        repo.create_playlist(conn, args.name, "folder" if args.folder else "playlist")
        print(f"created {'folder' if args.folder else 'playlist'}: {args.name}")
        return 0
    if pc == "list":
        for row in repo.list_playlists(conn):
            print(f"{row['id'][:8]}  {row['kind']:<8} {row['n']:>3} item(s)  {row['name']}")
        return 0
    pl = repo.find_playlist(conn, args.name)
    if pl is None:
        print(f"no playlist/folder named {args.name!r}", file=sys.stderr)
        return 1
    if pc == "show":
        for row in repo.list_episodes(conn, playlist_id=pl["id"]):
            print(_line(row))
    elif pc in ("add", "remove"):
        for ref in args.refs:
            ep = repo.find_episode(conn, ref)
            if ep is None:
                print(f"skip: no episode matches {ref!r}", file=sys.stderr)
                continue
            (repo.add_to_playlist if pc == "add" else repo.remove_from_playlist)(conn, pl["id"], ep["id"])
            print(f"{pc}: {ep['id'][:8]} {'->' if pc == 'add' else '<-'} {pl['name']}")
    elif pc == "rename":
        repo.rename_playlist(conn, pl["id"], args.new_name)
        print(f"renamed to {args.new_name}")
    elif pc == "delete":
        if not args.yes:
            print("this removes the playlist/folder only (episodes are kept). Re-run with --yes.", file=sys.stderr)
            return 2
        repo.delete_playlist(conn, pl["id"])
        print(f"deleted {pl['name']} (episodes kept)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    settings = get_settings()
    try:
        with repo.open_db(settings.db_path) as conn:
            if args.cmd == "list":
                pl = None
                if args.playlist:
                    pl = repo.find_playlist(conn, args.playlist)
                    if pl is None:
                        print(f"no playlist/folder named {args.playlist!r}", file=sys.stderr)
                        return 1
                for row in repo.list_episodes(conn, kind=args.kind, state=args.state, playlist_id=pl["id"] if pl else None):
                    print(_line(row))
            elif args.cmd == "show":
                row = repo.find_episode(conn, args.ref)
                if row is None:
                    print(f"no episode matches {args.ref!r}", file=sys.stderr)
                    return 1
                for key in row.keys():
                    print(f"{key}: {row[key]}")
                shorts = repo.child_shorts(conn, row["id"])
                if shorts:
                    print("shorts:")
                    for s in shorts:
                        print("  " + _line(s))
            elif args.cmd == "export":
                print(service.export_mp4(settings, conn, args.ref, dest_dir=args.to, name=args.name))
            elif args.cmd == "delete":
                row = repo.find_episode(conn, args.ref)
                if row is None:
                    print(f"no episode matches {args.ref!r}", file=sys.stderr)
                    return 1
                if not args.yes:
                    print(f"would delete: {_line(row)}\nRe-run with --yes to confirm (add --keep-files to keep the files).", file=sys.stderr)
                    return 2
                for path in service.delete_episode(settings, conn, args.ref, keep_files=args.keep_files, with_shorts=args.with_shorts):
                    print(f"removed {path}")
                print("deleted")
            elif args.cmd == "thumbnail":
                print(service.regenerate_thumbnail(settings, conn, args.ref, title=args.title, tag=args.tag,
                                                   subline=args.subline, frame_at=args.frame_at, base_image=args.image))
            elif args.cmd == "export-legacy":
                from life_lesson.library import legacy

                row = repo.find_episode(conn, args.ref)
                if row is None:
                    print(f"no episode matches {args.ref!r}", file=sys.stderr)
                    return 1
                if row["kind"] == "short":
                    if not args.shorts_dir:
                        print("a Short needs --shorts-dir (experiments/shorts/output)", file=sys.stderr)
                        return 2
                    print(legacy.export_short(settings, conn, args.ref, shorts_dir=args.shorts_dir))
                else:
                    if not args.videos_dir:
                        print("an episode needs --videos-dir (cartoon_storyboard/output/videos)", file=sys.stderr)
                        return 2
                    print(legacy.export_episode(settings, conn, args.ref, videos_dir=args.videos_dir))
            elif args.cmd == "description":
                print(service.rebuild_description(settings, conn, args.ref, full_url=args.full_url))
            elif args.cmd == "short":
                res = service.create_short(settings, conn, args.ref, full_url=args.full_url,
                                           offset=max(0, args.nth - 1), min_s=args.min, max_s=args.max, layout=args.layout)
                print(f"short: {res.episode_id[:8]}  {res.seconds:.0f}s  {res.title}\nvideo: {res.video_path}\npublish: {res.publish_dir}")
            elif args.cmd == "playlist":
                return _playlist(conn, args)
    except PipelineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
