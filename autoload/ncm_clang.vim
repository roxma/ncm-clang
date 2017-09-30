
fun! ncm_clang#compilation_info()
    py3 << EOF
import vim
import ncm_clang
from os import path
filepath = vim.eval("expand('%:p')")
filedir = path.dirname(filepath)
cwd = vim.eval("getcwd()")
args, directory = ncm_clang.args_from_cmake(filepath, cwd)
if not args:
    args, directory = ncm_clang.args_from_clang_complete(filepath, cwd)
ret = dict(args=args or [], directory=directory or cwd)
ret['args'] = ['-I' + filedir] + ret['args']
EOF
    return py3eval('ret')
endf

