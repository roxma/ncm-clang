
fun! ncm_clang#compilation_info()
    py3 << EOF
import vim
import ncm_clang
filepath = vim.eval("expand('%:p')")
cwd = vim.eval("getcwd()")
args, directory = ncm_clang.args_from_cmake(filepath, cwd)
if not args:
    args, directory = ncm_clang.args_from_clang_complete(filepath, cwd)
ret = dict(args=args or [], directory=directory or cwd)
EOF
    return py3eval('ret')
endf

