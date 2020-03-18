## This script will convert mixed line endings into just 1 uniform line ending appropriately.

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
