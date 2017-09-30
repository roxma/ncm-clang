## Introduction

clang completion integration for
[nvim-completion-manager](https://github.com/roxma/nvim-completion-manager)

![ncm-clang](https://user-images.githubusercontent.com/4538941/31041531-abd4a536-a5c9-11e7-9fbc-cbac0651089d.gif)

This plugin only support completion, for go to declaration support, and
others, you could try , for example,
[Rip-Rip/clang_complete](https://github.com/Rip-Rip/clang_complete)

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

### `ncm_clang#compilation_info()`

Get compilation flags and directory for current file.

