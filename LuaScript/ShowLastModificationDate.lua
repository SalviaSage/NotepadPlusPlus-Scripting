--- This will show the date the file was last modified in the status bar.

npp.AddEventHandler({"OnSave", "OnSwitchFile", "OnLangChange"}, function()
-- Make sure it is a "real" file first
	if npp:GetCurrentDirectory() == "" then
		return
	end

	local text = npp.LanguageDescription[npp.BufferLangType[npp.CurrentBufferID]] .. " | " .. "Edited: " .. os.date('%Y-%m-%d  %H:%M:%S', winfile.attributes(npp:GetFullCurrentPath(), "modification"))
	npp.StatusBar[STATUSBAR_DOC_TYPE] = text
end)
