## Highlights any white space that is only at the end of lines.

try :
	EWH__dict

except NameError :
	EWH__dict = dict()
	EWH__dict['indic_to_use'] = 10 ## pick a free indicator number
	def indicatorOptionsSet(indicator_number , indicator_style , rgb_color_tup , alpha , outline_alpha , draw_under_text , which_editor=editor) :
		which_editor.indicSetStyle(indicator_number , indicator_style) ## e.g. INDICATORSTYLE.ROUNDBOX
		which_editor.indicSetFore(indicator_number , rgb_color_tup)
		which_editor.indicSetAlpha(indicator_number , alpha) ## integer
		which_editor.indicSetOutlineAlpha(indicator_number , outline_alpha) ## integer
		which_editor.indicSetUnder(indicator_number , draw_under_text) ## boolean
	for editorX in (editor1 , editor2) :
		indicatorOptionsSet(EWH__dict['indic_to_use'] , INDICATORSTYLE.ROUNDBOX , (255 , 0 , 0) , 25 , 50 , True , editorX) ## white box rimmed in "pale violet red 2"
	def EWH__fileIsCloned(file_name_to_test) :
		retval = False
		clone_detect_dict = {}
		file_tup_list = notepad.getFiles()
		for tup in file_tup_list :
			(filename , _ , _ , _) = tup
			if filename not in clone_detect_dict :
				clone_detect_dict[filename] = 0
			else :
				clone_detect_dict[filename] += 1
				if filename == file_name_to_test : break
		if file_name_to_test in clone_detect_dict :
			if clone_detect_dict[file_name_to_test] >= 1 : retval = True
		return retval
	def EWH__fileIsClonedAndIsActiveInBothViews(file_name_to_test) :
		retval = False
		if editor1 and editor2 : ## both views are in use
			if EWH__fileIsCloned(file_name_to_test) :
				curr_doc_index_main_view = notepad.getCurrentDocIndex(0)
				curr_doc_index_2nd_view = notepad.getCurrentDocIndex(1)
				main_view_active_doc_bool = False
				secondary_view_active_doc_bool = False
				file_tup_list = notepad.getFiles()
				for tup in file_tup_list :
					(filename , _ , index_in_view , view_number) = tup
					if filename == file_name_to_test :
						if view_number == 0 :
							if index_in_view == curr_doc_index_main_view :
								main_view_active_doc_bool = True
						elif view_number == 1 :
							if index_in_view == curr_doc_index_2nd_view :
								secondary_view_active_doc_bool = True
						if main_view_active_doc_bool and secondary_view_active_doc_bool :
							retval = True
							break
		return retval
	def EWH__getViewableEditorAndRangeTupleListList(work_across_both_views) :
		retval = []
		## retval looks like these examples:
		## [(editor , [(0 , 1000) , (2020 , 3000)])]
		## [(editor1 , [(0 , 1000) , (2020 , 3000)]) , (editor2 , [(4000 , 5000) , (6020 , 7000)])]
		def consolidate_range_tuple_list(range_tup_list) :
			sorted_range_tup_list = sorted(range_tup_list) ## sort criteria is first element of tuple in list
			saved_2element_list = list(sorted_range_tup_list[0])
			for (start , end) in sorted_range_tup_list :
				if start <= saved_2element_list[1] :
					saved_2element_list[1] = max(saved_2element_list[1] , end)
				else :
					yield tuple(saved_2element_list)
					saved_2element_list[0] = start
					saved_2element_list[1] = end
			yield tuple(saved_2element_list)
		def get_onscreen_pos_tup_list(which_editor) : ## which_editor is editor1 or editor2 (or maybe even just plain editor) ## loosely based upon the N++ source for SmartHighlighter::highlightViewWithWord()
			retval_tup_list = list()
			temp_tup_list = []
			MAXLINEHIGHLIGHT = 400
			firstLine = which_editor.getFirstVisibleLine()
			currentLine = firstLine
			nbLineOnScreen = which_editor.linesOnScreen()
			nrLines = min(nbLineOnScreen , MAXLINEHIGHLIGHT) + 1
			lastLine = firstLine + nrLines
			prevDocLineChecked = -1
			break_out = False
			while currentLine < lastLine :
				docLine = which_editor.docLineFromVisible(currentLine)
				if docLine != prevDocLineChecked :
					prevDocLineChecked = docLine
					startPos = which_editor.positionFromLine(docLine)
					endPos = which_editor.positionFromLine(docLine + 1)
					if endPos == -1 :
						endPos = which_editor.getTextLength() - 1
						break_out = True
					if endPos > startPos : temp_tup_list.append((startPos , endPos))
					if break_out : break
				currentLine += 1
			if len(temp_tup_list) > 0 :
				retval_tup_list = list(consolidate_range_tuple_list(temp_tup_list))
			return retval_tup_list
		both_views_open = True if editor1 and editor2 else False
		curr_file_active_in_both_views = EWH__fileIsClonedAndIsActiveInBothViews(notepad.getCurrentFilename())
#		if both_views_open else False
		if both_views_open :
			ed1_range_tup_list = get_onscreen_pos_tup_list(editor1)
			ed2_range_tup_list = get_onscreen_pos_tup_list(editor2)
		if curr_file_active_in_both_views :
			range_tup_list = list(consolidate_range_tuple_list(ed1_range_tup_list + ed2_range_tup_list))
			retval.append((editor , range_tup_list))
		elif both_views_open and work_across_both_views :
			retval.append((editor1 , ed1_range_tup_list))
			retval.append((editor2 , ed2_range_tup_list))
		else :
			range_tup_list = get_onscreen_pos_tup_list(editor)
			retval.append((editor , range_tup_list))
		return retval
	def EWH__callback_sci_UPDATEUI(args) :
		for (editorX , pos_range_tuple_list) in EWH__getViewableEditorAndRangeTupleListList(True) : ## clear out any existing highlighting in areas the user can currently see
			for (start_pos , end_pos) in pos_range_tuple_list :
				editorX.setIndicatorCurrent(EWH__dict['indic_to_use'])
				editorX.indicatorClearRange(start_pos , end_pos - start_pos)
			def eolws_hilite_regex_search_match_found_callback(m) :
				(span_start , span_end) = m.span()
				editorX.setIndicatorCurrent(EWH__dict['indic_to_use'])
				editorX.indicatorFillRange(span_start , span_end - span_start)
			for (start_pos , end_pos) in pos_range_tuple_list :
				editorX.research (
					r'\h+$' ,
					eolws_hilite_regex_search_match_found_callback ,
					0 , #re.IGNORECASE ,
					start_pos ,
					end_pos )
	editor.callbackSync(EWH__callback_sci_UPDATEUI , [SCINTILLANOTIFICATION.UPDATEUI]) ## install callback

else :
	editor.setSelectionMode(editor.getSelectionMode()) ## force manual UPDATEUI to happen
