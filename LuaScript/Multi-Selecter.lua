--- Makes it so that pressing ctrl+alt+d jumps to the next same word within view.

npp.AddShortcut("Selection Add Next", "Ctrl+Alt+D", function()
    editor:MultipleSelectAddNext()
end)
