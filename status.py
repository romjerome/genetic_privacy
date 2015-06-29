"""status message. just call it, it'll work. hopefully."""

import sys, time, math
from itertools import *

class State:
	def __init__(self):
		self.cnt = 0
		self.lastloc = [None, "", -1] 
		self.lastwritetime = 0
		self.lastinvoctime = 0
		self.starttime = 0
		self.dirty = False
		self.timeperitem = None

_state = State()

#FIXME: divide total by bucketlen
def wrap(items, msg=None, total=None, bucketlength=1,  inspect=True):
	#FIXME: change bucketlen to something better
	if total is None and hasattr(items, "__len__"):
		total = len(items)
	for item, cnt in izip(items, count(1)):
		yield item
		if cnt % bucketlength == 0:
			status(msg, total, val=cnt, 
					done=cnt==total if total else None, 
					depth=2, inspect=inspect)

def status(msg=None, total=None, val=None, done=None, depth=1, inspect=True):
	"""
	intelligently displays a continually updated status message
	if done is true this is the last message in this series
	if sameframe is false, then you can call it from different invocations of the
	function and it will treat it as the same series

	depth is an internal parameter which should be 2 in case it is being wrapped
	"""

	#TODO: stabilize over time
	
	global _state
	if inspect:
		frame = sys._getframe(depth)
		location = [frame, frame.f_code.co_filename, frame.f_lineno]
	else:
		location = None
	
	def newloc():
		if _state.dirty:
			sys.stderr.write("\n")
			_state.dirty = False
		_state.lastloc = location
		_state.cnt = 0
		_state.starttime = time.time()

	def writelast():
		writemsg()
		sys.stderr.write("\n")
		_state.dirty = False
		_state.cnt = 0
	
	def writemsg():
		frac = total and float(val if val is not None else  _state.cnt)/total or 0
		timespent = time.time()-_state.starttime
		sys.stderr.write("\r%s %s%s [%ds%s]" % 
			(msg if msg else (frame.f_code.co_name if inspect else ''),
			val if val is not None else "%d" %_state.cnt,
			total and "/%d (%.2f%%)" % (total, 100 * frac) or "",
			int(timespent+0.5), 
			", %ds left" % int((total - _state.cnt) * _state.timeperitem) if (total and _state.timeperitem) else ""))
		_state.dirty = True
		_state.lastwritetime = time.time()
	
	_state.cnt += 1
	if _state.timeperitem is None and _state.lastinvoctime > 0:
		_state.timeperitem = time.time() - _state.lastinvoctime
	elif _state.timeperitem is not None:
		beta = math.log(_state.cnt+1,2) / (_state.cnt + 1)
		current_tpi = time.time() - _state.lastinvoctime
		_state.timeperitem = (1-beta) * _state.timeperitem + beta * current_tpi
	if location != _state.lastloc and not done: newloc()
	if total and _state.cnt >= total and done is None: done = True
	if time.time() - _state.lastwritetime > 0.05 and not done: writemsg()
	if done: writelast()
	_state.lastinvoctime = time.time()

