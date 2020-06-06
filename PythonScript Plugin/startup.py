# The lines up to and including sys.stderr should always come first
# Then any errors that occur later get reported to the console
# If you'd prefer to report errors to a file, you can do that instead here.
import sys
from Npp import *

# Set the stderr to the normal console as early as possible, in case of early errors
sys.stderr = console

# Define a class for writing to the console in red
class ConsoleError:
	def __init__(self):
		global console
		self._console = console;

	def write(self, text):
		self._console.writeError(text);

# Set the stderr to write errors in red
sys.stderr = ConsoleError()

# This imports the "normal" functions, including "help"
import site

sys.stdout = console

# In order to set the stdout to the current active document, uncomment the following line
# sys.stdout = editor
# So print "hello world", will insert "hello world" at the current cursor position

## SCRIPT 1 START ## Adds the zoom indicator to the statusbar.
import locale
locale.setlocale(locale.LC_ALL , '')

def StatusbarEOLOverride(args) :
	_eolMode = editor.getEOLMode()
	_zoom = editor.getZoom()
	_eolString = ""
	_zoomString = ""
	if _eolMode == 0 :
		_eolString = "CR+LF"
	elif _eolMode == 1 :
		_eolString = "CR"
	elif _eolMode == 2 :
		_eolString = "LF"
	if _zoom == 0 :
		_zoomString = "0"
	else :
		_zoomString = '{:+}'.format(_zoom)
	notepad.setStatusBar(STATUSBARSECTION.EOFFORMAT , '{} | Zoom: {}' .format(_eolString , _zoomString))

editor.callback(StatusbarEOLOverride , [SCINTILLANOTIFICATION.UPDATEUI , SCINTILLANOTIFICATION.ZOOM]) ## register callback
## SCRIPT 1 END

## SCRIPT 2 START ## Makes the caret a block caret in the override mode.
CARETSTYLE_OVERSTRIKE_BLOCK = 16
editor1.setCaretStyle(CARETSTYLE_OVERSTRIKE_BLOCK)
editor2.setCaretStyle(CARETSTYLE_OVERSTRIKE_BLOCK)

## SCRIPT 2 END

## SCRIPT 3 START ## Highlights line final whitespace

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
		#if both_views_open else False
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

## SCRIPT 3 END ## Highlights line final whitespace

## SCRIPT 4 START ## Highlights inside of brackets.
try:

	BH__dict

except NameError:

	BH__dict = dict()

	BH__dict['indic_for_box_at_caret'] = 11  # pick a free indicator number

	def indicatorOptionsSet(indicator_number, indicator_style, rgb_color_tup, alpha, outline_alpha, draw_under_text, which_editor=editor):
		which_editor.indicSetStyle(indicator_number, indicator_style)       # e.g. INDICATORSTYLE.ROUNDBOX
		which_editor.indicSetFore(indicator_number, rgb_color_tup)
		which_editor.indicSetAlpha(indicator_number, alpha)                 # integer
		which_editor.indicSetOutlineAlpha(indicator_number, outline_alpha)  # integer
		which_editor.indicSetUnder(indicator_number, draw_under_text)       # boolean

	for editorX in (editor1, editor2):
		indicatorOptionsSet(BH__dict['indic_for_box_at_caret'], INDICATORSTYLE.STRAIGHTBOX, (238,121,159), 0, 255, True, editorX)  # white box rimmed in "pale violet red 2"
		#indicatorOptionsSet(BH__dict['indic_for_box_at_caret'], INDICATORSTYLE.STRAIGHTBOX, (255, 255, 0), 100, 50, True, editorX)

	BH__dict['last_modificationType_for_hack'] = None

	def BH__containing_box_indices_into_string(str_containing_caret, caret_index_into_str):

		class Stack:
			def __init__(self): self.clear()
			def isEmpty(self): return self.size() == 0
			def push(self, item): self.items.append(item)
			def pop(self): return None if self.size() == 0 else self.items.pop()
			def peek(self): return None if self.size() == 0 else self.items[self.size() - 1]
			def size(self): return len(self.items)
			def clear(self): self.items = []

		retval = (None, None)  # default to no valid box

		get_opening_char_via_closing_char_dict = {
			')' : '(',
			']' : '[',
			'}' : '{',
			}
		get_closing_char_via_opening_char_dict = dict((v, k) for (k, v) in get_opening_char_via_closing_char_dict.items())

		closing_chars = get_opening_char_via_closing_char_dict.keys()
		opening_chars = get_opening_char_via_closing_char_dict.values()

		box_ending_index = -1
		box_starting_index = -1

		stack = Stack()

		for j in range(caret_index_into_str, len(str_containing_caret)):
			c = str_containing_caret[j]
			if c in closing_chars:
				if stack.isEmpty():
					box_ending_index = j
					break
				else:
					if stack.peek() ==  get_opening_char_via_closing_char_dict[c]:
						stack.pop()
					else:
						break  # unbalanced
			elif c in opening_chars:
				stack.push(c)

		if box_ending_index != -1:
			stack.clear()
			box_starting_index = -1
			for j in range(caret_index_into_str - 1, -1, -1):
				c = str_containing_caret[j]
				if c in opening_chars:
					if stack.isEmpty():
						box_starting_index = j
						break
					else:
						if stack.peek() ==  get_closing_char_via_opening_char_dict[c]:
							stack.pop()
						else:
							break  # unbalanced
				elif c in closing_chars:
					stack.push(c)

		if box_ending_index != -1:
			if box_starting_index != -1:
				if str_containing_caret[box_ending_index] == get_closing_char_via_opening_char_dict[str_containing_caret[box_starting_index]]:
					retval = (box_starting_index, box_ending_index + 1)

		return retval

	def BH__callback_sci_MODIFIED(args):
		global BH__dict
		BH__dict['last_modificationType_for_hack'] = args['modificationType']

	def BH__fileIsCloned(file_name_to_test):
		retval = False
		clone_detect_dict = {}
		file_tup_list = notepad.getFiles()
		for tup in file_tup_list:
			(filename, _, _, _) = tup
			if filename not in clone_detect_dict:
				clone_detect_dict[filename] = 0
			else:
				clone_detect_dict[filename] += 1
				if filename == file_name_to_test: break
		if file_name_to_test in clone_detect_dict:
			if clone_detect_dict[file_name_to_test] >= 1: retval = True
		return retval

	def BH__fileIsClonedAndIsActiveInBothViews(file_name_to_test):
		retval = False
		if editor1 and editor2:
			# both views are in use
			if BH__fileIsCloned(file_name_to_test):
				curr_doc_index_main_view = notepad.getCurrentDocIndex(0)
				curr_doc_index_2nd_view = notepad.getCurrentDocIndex(1)
				main_view_active_doc_bool = False
				secondary_view_active_doc_bool = False
				file_tup_list = notepad.getFiles()
				for tup in file_tup_list:
					(filename, _, index_in_view, view_number) = tup
					if filename == file_name_to_test:
						if view_number == 0:
							if index_in_view == curr_doc_index_main_view:
								main_view_active_doc_bool = True
						elif view_number == 1:
							if index_in_view == curr_doc_index_2nd_view:
								secondary_view_active_doc_bool = True
						if main_view_active_doc_bool and secondary_view_active_doc_bool:
							retval = True
							break
		return retval

	def BH__getViewableEditorAndRangeTupleListList(work_across_both_views):
		retval = []
		# retval looks like these examples:
		#  [ ( editor, [ (0, 1000), (2020, 3000) ] ) ]
		#  [ ( editor1, [ (0, 1000), (2020, 3000) ] ), ( editor2, [ (4000, 5000), (6020, 7000) ] ) ]
		def consolidate_range_tuple_list(range_tup_list):
			sorted_range_tup_list = sorted(range_tup_list)  # sort criteria is first element of tuple in list
			saved_2element_list = list(sorted_range_tup_list[0])
			for (start, end) in sorted_range_tup_list:
				if start <= saved_2element_list[1]:
					saved_2element_list[1] = max(saved_2element_list[1], end)
				else:
					yield tuple(saved_2element_list)
					saved_2element_list[0] = start
					saved_2element_list[1] = end
			yield tuple(saved_2element_list)
		def get_onscreen_pos_tup_list(which_editor):  # which_editor is editor1 or editor2 (or maybe even just plain editor)
			# loosely based upon the N++ source for SmartHighlighter::highlightViewWithWord()
			retval_tup_list = list()
			temp_tup_list = []
			MAXLINEHIGHLIGHT = 400
			firstLine = which_editor.getFirstVisibleLine()
			currentLine = firstLine
			nbLineOnScreen = which_editor.linesOnScreen()
			nrLines = min(nbLineOnScreen, MAXLINEHIGHLIGHT) + 1
			lastLine = firstLine + nrLines
			prevDocLineChecked = -1
			break_out = False
			while currentLine < lastLine:
				docLine = which_editor.docLineFromVisible(currentLine)
				if docLine != prevDocLineChecked:
					prevDocLineChecked = docLine
					startPos = which_editor.positionFromLine(docLine)
					endPos = which_editor.positionFromLine(docLine + 1)
					if endPos == -1:
						endPos = which_editor.getTextLength() - 1
						break_out = True
					if endPos > startPos: temp_tup_list.append((startPos, endPos))
					if break_out: break
				currentLine += 1
			if len(temp_tup_list) > 0:
				retval_tup_list = list(consolidate_range_tuple_list(temp_tup_list))
			return retval_tup_list
		both_views_open = True if editor1 and editor2 else False
		curr_file_active_in_both_views = BH__fileIsClonedAndIsActiveInBothViews(notepad.getCurrentFilename()) if both_views_open else False
		if both_views_open:
			ed1_range_tup_list = get_onscreen_pos_tup_list(editor1)
			ed2_range_tup_list = get_onscreen_pos_tup_list(editor2)
		if curr_file_active_in_both_views:
			range_tup_list = list(consolidate_range_tuple_list(ed1_range_tup_list + ed2_range_tup_list))
			retval.append((editor, range_tup_list))
		elif both_views_open and work_across_both_views:
			retval.append((editor1, ed1_range_tup_list))
			retval.append((editor2, ed2_range_tup_list))
		else:
			range_tup_list = get_onscreen_pos_tup_list(editor)
			retval.append((editor, range_tup_list))
		return retval

	def BH__callback_sci_UPDATEUI(args):

		# hack, see https://notepad-plus-plus.org/community/topic/12360/vi-simulator-how-to-highlight-a-word/27, look for "16400" in code:
		if args['updated'] == UPDATE.CONTENT and BH__dict['last_modificationType_for_hack'] == (MODIFICATIONFLAGS.CHANGEINDICATOR | MODIFICATIONFLAGS.USER): return

		for (editorX, pos_range_tuple_list) in BH__getViewableEditorAndRangeTupleListList(True):

			# clear out any existing highlighting in areas the user can currently see
			for (start_pos, end_pos) in pos_range_tuple_list:
				editorX.setIndicatorCurrent(BH__dict['indic_for_box_at_caret'])
				editorX.indicatorClearRange(start_pos, end_pos - start_pos)

			for (start_pos, end_pos) in pos_range_tuple_list:

				if start_pos <= editorX.getCurrentPos() <= end_pos:

					(box_start_offset, box_end_offset) = BH__containing_box_indices_into_string(
						editorX.getTextRange(start_pos, end_pos),
						editorX.getCurrentPos() - start_pos
						)

					if box_start_offset != None:
						size_of_box_in_chars = box_end_offset - box_start_offset
						if size_of_box_in_chars <= 2:
							pass  # rather pointless to box in if the opening and closing delims are right next to each other
						else:
							editorX.setIndicatorCurrent(BH__dict['indic_for_box_at_caret'])
							editorX.indicatorFillRange(start_pos + box_start_offset, size_of_box_in_chars)

	editor.callbackSync(BH__callback_sci_UPDATEUI, [SCINTILLANOTIFICATION.UPDATEUI])  # install callback
	editor.callbackSync(BH__callback_sci_MODIFIED, [SCINTILLANOTIFICATION.MODIFIED])  # may not need to be "Sync", but for now we'll make it that way

else:

	editor.setSelectionMode(editor.getSelectionMode())  # force manual UPDATEUI to happen
	## SCRIPT 4 END ## Highlights inside of brackets.

	## SCRIPT 5 START ## LINE ENDING REPAIR AT SAVE ## Converts mismatching line endings to the uniform.
try:
	LERAS__bad_eol_regex_via_good_eol_dict

except NameError:
	LERAS__bad_eol_regex_via_good_eol_dict = {
		'\r\n' : r'\r(?!\n)|(?<!\r)\n' ,
		'\n'   : r'\r\n?' ,
		'\r'   : r'\r?\n' ,
	}
	def LERAS__callback_npp_FILEBEFORESAVE(args):
		notepad.activateBufferID(args['bufferID'])
		correct_eol_for_this_file = ['\r\n', '\r', '\n'][notepad.getFormatType()]
		editor.rereplace(LERAS__bad_eol_regex_via_good_eol_dict[correct_eol_for_this_file], correct_eol_for_this_file)
	notepad.callback(LERAS__callback_npp_FILEBEFORESAVE , [NOTIFICATION.FILEBEFORESAVE])

	## SCRIPT 5 END


