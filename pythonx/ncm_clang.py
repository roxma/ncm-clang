from cm import getLogger
from os.path import dirname, join, isfile
from pathlib import Path
import shlex
import json

logger = getLogger(__name__)


def args_from_cmake(filepath, cwd):
    filedir = dirname(filepath)

    files = ['compile_commands.json', 'build/compile_commands.json']
    cfg_path = find_config([filedir, cwd], files)

    if not cfg_path:
        return None, None

    try:
        with open(cfg_path, "r") as f:
            txt = f.read()
            commands = json.loads(txt)
            for cmd in commands:
                if cmd['file'] == filepath:
                    logger.info("compile_commands: %s", cmd)
                    return shlex.split(cmd['command'])[1:-1], cmd['directory']

            logger.error("Failed finding args from %s for %s", cfg_path, filepath)

            # Merge all include dirs and the flags of the last item as a
            # fallback. This is useful for editting header file.
            all_dirs = {}
            args = []
            for cmd in commands:
                args = shlex.split(cmd['command'])[1:-1]
                add_next = False
                for arg in args:
                    if add_next:
                        add_next = False
                        all_dirs['-I' + arg] = True
                    if arg == "-I":
                        add_next = True
                        continue
                    if arg.startswith("-I"):
                        all_dirs['-I' + arg[2:]] = True

            return list(all_dirs.keys()) + args, filedir

    except Exception as ex:
        logger.exception("read compile_commands.json [%s] failed.", cfg_path)

    return None, None


def args_from_clang_complete(filepath, cwd):
    filedir = dirname(filepath)

    clang_complete = find_config([filedir, cwd], '.clang_complete')

    if not clang_complete:
        return None, None

    try:
        with open(clang_complete, "r") as f:
            clang_complete_args = shlex.split(" ".join(f.readlines()))
            logger.info('.clang_complete args: %s', clang_complete_args)
            return clang_complete_args, dirname(clang_complete)
    except Exception as ex:
        logger.exception("read config file %s failed.", clang_complete)

    return None, None


def find_config(bases, names):
    if isinstance(names, str):
        names = [names]

    if isinstance(bases, str):
        bases = [bases]

    for base in bases:
        r = Path(base).resolve()
        dirs = [r] + list(r.parents)
        for d in dirs:
            d = str(d)
            for name in names:
                p = join(d, name)
                if isfile(p):
                    return p

    return None
