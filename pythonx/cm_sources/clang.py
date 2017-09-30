# -*- coding: utf-8 -*-

# For debugging, use this command to start neovim:
#
# NVIM_PYTHON_LOG_FILE=nvim.log NVIM_PYTHON_LOG_LEVEL=INFO nvim
#
#
# Please register source before executing any other code, this allow cm_core to
# read basic information about the source without loading the whole module, and
# modules required by this module
from cm import register_source, getLogger, Base

register_source(name='clang',
                priority=9,
                abbreviation='',
                scoping=True,
                scopes=['cpp'],
                early_cache=1,
                cm_refresh_patterns=[r'-\>', r'::', r'\.'],)

import subprocess
import re
import shlex
from os import path
import json

logger = getLogger(__name__)


class Source(Base):

    def __init__(self, nvim):
        super(Source, self).__init__(nvim)

        self._clang_path = 'clang++'

    def cm_refresh(self, info, ctx, *args):

        src = self.get_src(ctx).encode('utf-8')
        lnum = ctx['lnum']
        col = ctx['col']
        filepath = ctx['filepath']
        startcol = ctx['startcol']
        cwd = cwd=self.nvim.eval('getcwd()')
        filedir = path.dirname(filepath)

        run_dir = cwd

        args = [ self._clang_path,
                '-x', 'c++',
                '-fsyntax-only',
                '-Xclang', '-code-completion-macros',
                # '-Xclang', '-code-completion-brief-comments',
                # Perfer external snippets instead of -code-completion-patterns
                # '-Xclang', '-code-completion-patterns',
                '-Xclang', '-code-completion-at={}:{}:{}'.format('-', lnum, col),
                '-',
                '-I', filedir
                ]

        cmake_args, directory = self.get_cmake_args(filepath, filedir, cwd)
        if cmake_args is not None:
            args += cmake_args
            run_dir = directory
        else:
            clang_complete_args, directory = self.get_clang_complete_args(filedir, cwd)
            if clang_complete_args:
                args += clang_complete_args
                run_dir = directory

        # args = args + self._clang_opts
        logger.debug("args: %s", args)

        proc = subprocess.Popen(args=args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL,
                                cwd=run_dir)

        result, errs = proc.communicate(src, timeout=30)

        result = result.decode()

        logger.debug("result: [%s]", result)

        matches = []

        for line in result.split("\n"):
            # COMPLETION: cout : [#ostream#]cout
            # COMPLETION: terminate : [#void#]terminate()
            if not line.startswith("COMPLETION: "):
                continue
            
            try:
                m = self.parse_completion(line)
                matches.append(m)
            except Exception as ex:
                logger.exception("failed parsing completion: %s", line)

        logger.debug("startcol: %s, matches: %s", startcol, matches)

        self.complete(info, ctx, startcol, matches)

    def parse_completion(self, line):
        m = re.search(r'^COMPLETION:\s+([\w~&=!*/_]+)(\s+:\s+(.*)$)?', line)
        word = m.group(1)

        menu = ''
        snippet = ''
        is_snippet = False
        snippet_num = 0

        if m.group(3):
            # [#double#]copysign(<#double __x#>, <#double __y#>)
            more = m.group(3)
            menu = re.sub(r'\[#([^#]+)#\]', r'\1 ', more)
            menu = menu.replace('<#', '')
            menu = menu.replace('#>', '')
            menu = menu.replace('{#', '')
            menu = menu.replace('#}', '')

            def rep(m):
                nonlocal is_snippet
                nonlocal snippet_num
                is_snippet = True
                snippet_num += 1
                name = m.group(1)
                last_word =re.search('([\w_]+)$', name)
                if last_word:
                    name = last_word.group(1)
                return self.snippet_placeholder(snippet_num, name)

            snippet = re.sub(r'\[#([^#]+)#\]', r'', more)
            snippet = re.sub(r'\<#([^#]+)#\>', rep, snippet)

            begin = None
            end = None
            mb = re.search('\<#', more)
            me = re.search('.*#\>', more) # greedy
            if mb:
                begin = mb.start()
            if me:
                end = mb.end()

            opt_begin = None
            opt_end = None
            mob = re.search('\{#', more)
            moe = re.search('.*#\}', more)
            if mob:
                opt_begin = mob.start()
            if moe:
                opt_end = moe.end()

            if opt_begin:
                if opt_begin < begin and opt_end > end:
                    snippet = re.sub(r'\{#.*#\}', self.snippet_placeholder(1), snippet)
                else:
                    snippet = re.sub(r'\{#.*#\}', '', snippet)

        if is_snippet:
            return dict(word=word, menu=menu, snippet=snippet)
        else:
            return dict(word=word, menu=menu)

    def get_cmake_args(self, filepath, filedir, cwd):

        compile_commands = find_config([filedir, cwd], 'compile_commands.json')
        if not compile_commands:
            compile_commands = find_config([filedir, cwd], 'build/compile_commands.json')

        if not compile_commands:
            return None, None

        try:
            with open (compile_commands, "r") as f:
                txt = f.read()
                commands = json.loads(txt)
                for cmd in commands:
                    if cmd['file'] == filepath:
                        logger.info("compile_commands: %s", cmd)
                        return shlex.split(cmd['command'])[1:-1], cmd['directory']
                logger.error("Failed finding args from %s for %s", compile_commands, filepath)
        except Exception as ex:
            logger.exception("read %s failed.", compile_commands)

        return None, None


    def get_clang_complete_args(self, filedir, cwd):

        clang_complete = find_config([filedir, cwd], '.clang_complete')

        if not clang_complete:
            return None, None

        try:
            with open (clang_complete, "r") as f:
                clang_complete_args = shlex.split(" ".join(f.readlines()))
                logger.info('.clang_complete args: %s', clang_complete_args)
                return clang_complete_args, path.dirname(clang_complete)
        except Exception as ex:
            logger.exception("read config file %s failed.", clang_complete)

        return None, None

def find_config(bases, name):
    from pathlib import Path

    if type(bases) == type(""):
        bases = [bases]

    for base in bases:
        r = Path(base).resolve()
        dirs = [r] + list(r.parents)
        for d in dirs:
            d = str(d)
            p = path.join(d, name)
            if path.isfile(p):
                return p

    return None

