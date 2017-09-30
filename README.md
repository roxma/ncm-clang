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

The following vimrc shows how to use
[Rip-Rip/clang_complete](https://github.com/Rip-Rip/clang_complete)'s goto
declaration feature.

```vim
    " default key mapping is annoying
    let g:clang_make_default_keymappings = 0
    " ncm-clang is auto detecting compile_commands.json and .clang_complete
    " file
    let g:clang_auto_user_options = ''

    func WrapClangGoTo()
        let cwd = getcwd()
        let info = ncm_clang#compilation_info()
        exec 'cd ' . info['directory']
        try
            let b:clang_user_options = join(info['args'], ' ')
            call g:ClangGotoDeclaration()
        catch
        endtry
        " restore
        exec 'cd ' . cwd
    endfunc

    " map to gd key
    autocmd FileType c,cpp nnoremap <buffer> gd :call WrapClangGoTo()<CR>
```

The following vimrc shows how to work with [w0rp/ale](https://github.com/w0rp/ale)

```vim
    let g:ale_linters = {
        \   'cpp': ['clang'],
        \}
    autocmd BufEnter *.cpp,*.h,*.hpp,*.hxx let g:ale_cpp_clang_options = join(ncm_clang#compilation_info()['args'], ' ')
```
