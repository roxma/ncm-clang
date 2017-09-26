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
                cm_refresh_patterns=[r'-\>', r'::'],)

import subprocess
import re

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

        args = [ self._clang_path,
                '-x', 'c++',
                '-fsyntax-only',
                '-Xclang', '-code-completion-macros',
                '-Xclang', '-code-completion-at={}:{}:{}'.format('-', lnum, col),
                '-'
                ]
        # args = args + self._clang_opts
        logger.debug("args: %s", args)

        proc = subprocess.Popen(args=args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL,
                                cwd=self.nvim.eval('getcwd()'))

        result, errs = proc.communicate(src, timeout=30)

        result = result.decode()

        logger.debug("result: [%s]", result)

        matches = []

        for line in result.split("\n"):
            # COMPLETION: cout : [#ostream#]cout
            # COMPLETION: terminate : [#void#]terminate()
            if not line.startswith("COMPLETION: "):
                continue

            m = re.search('^COMPLETION: (\w+)', line)

            word = m.group(1)
            matches.append(word)

        self.complete(info, ctx, startcol, matches)
