
if get(g:, 'ncm_clang#loaded', 0)
    finish
endif

let g:ncm_clang#loaded = 1

let g:ncm_clang#database_paths = get(g:, 'ncm_clang#database_paths', ['compile_commands.json', 'build/compile_commands.json'])

fun! ncm_clang#compilation_info()
    py3 << EOF
import vim
import ncm_clang
from os import path
filepath = vim.eval("expand('%:p')")
filedir = path.dirname(filepath)
cwd, database_paths = vim.eval("ncm_clang#_context()")
args, directory = ncm_clang.args_from_cmake(filepath, cwd, database_paths)
if not args:
    args, directory = ncm_clang.args_from_clang_complete(filepath, cwd)
ret = dict(args=args or [], directory=directory or cwd)
ret['args'] = ['-I' + filedir] + ret['args']
EOF
    return py3eval('ret')
endf

func! ncm_clang#_context()
    return  [getcwd(), g:ncm_clang#database_paths]
endfunc

