## Adds the zoom indicator to the statusbar.
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
