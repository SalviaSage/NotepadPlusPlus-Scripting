--- SCRIPT 1 START -- Makes spaces have no symbols while keeping the symbols for tabs

editor.WhitespaceSize = 0

--- SCRIPT 1 END

--- SCRIPT 2 START -- ADDS LAST MODIFIED DATE TO THE STATUS BAR

npp.AddEventHandler({"OnSave", "OnSwitchFile", "OnLangChange"}, function()
-- Make sure it is a "real" file first
	if npp:GetCurrentDirectory() == "" then
		return
	end

	local text = npp.LanguageDescription[npp.BufferLangType[npp.CurrentBufferID]] .. " | " .. "Edited: " .. os.date('%Y-%m-%d  %H:%M:%S', winfile.attributes(npp:GetFullCurrentPath(), "modification"))
	npp.StatusBar[STATUSBAR_DOC_TYPE] = text
end)

--- SCRIPT 2 END

--- SCRIPT 3 START

npp.AddShortcut("Selection Add Next", "Ctrl+Alt+D", function()
    editor:MultipleSelectAddNext()
end)

--- SCRIPT 3 END
