## Introduction

clang completion integration for
[nvim-completion-manager](https://github.com/roxma/nvim-completion-manager)

![ncm-clang](https://user-images.githubusercontent.com/4538941/31041531-abd4a536-a5c9-11e7-9fbc-cbac0651089d.gif)

This plugin only support completion, for go to declaration support, and
others, you could try , for example,
[osyo-manga/vim-snowdrop](https://github.com/osyo-manga/vim-snowdrop)

## Requirements

- `clang` in your `$PATH`

## Installation

Assuming you're using [vim-plug](https://github.com/junegunn/vim-plug)

```vim
Plug 'roxma/ncm-clang'
```

## Settings

If you're using cmake, add `set(CMAKE_EXPORT_COMPILE_COMMANDS, 1)` into
`CMakeLists.txt` so that `compile_commands.json` will be generated.

If your project is not using cmake, store the compile flags into a file named
`.clang_complete`.

## Utilities

This example shows how to auto detect compilation falgs for vim-snowdrop.

```vim
func DetectConfig()
    py3 << EOF
import vim
import ncm_clang
filepath = vim.eval("expand('%:p')")
cwd = vim.eval("getcwd()")
args, _ = ncm_clang.args_from_cmake(filepath, cwd)
if not args:
    args, _ = ncm_clang.args_from_clang_complete(filepath, cwd)
vim.vars['snowdrop#command_options'] = {
    'cpp': " ".join(args or [])
}
EOF
endfunc
autocmd FileType cpp,c call DetectConfig()
```

