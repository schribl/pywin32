# hierlist
#
# IMPORTANT - Please read before using.

# This module exposes an API for a Hierarchical Tree Control.
# Previously, a custom tree control was included in Pythonwin which
# has an API very similar to this.

# The current control used is the common "Tree Control".  This module exists now
# to provide an API similar to the old control, but for the new Tree control.

# If you need to use the Tree Control, you may still find this API a reasonable
# choice.  However, you should investigate using the tree control directly
# to provide maximum flexibility (but with extra work).


import win32ui 
import win32con
from win32api import RGB

from pywin.mfc import object, window, docview, dialog
import commctrl

# helper to get the text of an arbitary item
def GetItemText(item):
	if type(item)==type(()) or type(item)==type([]):
		use = item[0]
	else:
		use = item
	if type(use)==type(''):
		return use
	else:
		return repr(item)

	
class HierDialog(dialog.Dialog):
	def __init__(self, title, hierList, bitmapID = win32ui.IDB_HIERFOLDERS, dlgID = win32ui.IDD_TREE, dll = None, childListBoxID = win32ui.IDC_LIST1):
		dialog.Dialog.__init__(self, dlgID, dll )	# reuse this dialog.
		self.hierList=hierList
		self.dlgID = dlgID
		self.title=title
#		self.childListBoxID = childListBoxID
	def OnInitDialog(self):
		self.SetWindowText(self.title)
		self.hierList.HierInit(self)
		return dialog.Dialog.OnInitDialog(self)

class HierList(object.Object):
	def __init__(self, root, bitmapID = win32ui.IDB_HIERFOLDERS, listBoxId = None, bitmapMask = None): # used to create object.
		self.list = self._obj_ = None
		self.bitmapID = bitmapID
		self.root = root
		self.listBoxId = listBoxId
		self.itemHandleMap = {}
		self.filledItemHandlesMap = {}
		self.bitmapMask = bitmapMask 
	def ItemFromHandle(self, handle):
		return self.itemHandleMap[handle]
	def SetStyle(self, newStyle):
		import win32api
		hwnd = self._obj_.GetSafeHwnd()
		style = win32api.GetWindowLong(hwnd, win32con.GWL_STYLE);
		win32api.SetWindowLong(hwnd, win32con.GWL_STYLE, (style | newStyle) )

	def HierInit(self, parent, listControl = None ):	# Used when window first exists.
		# this also calls "Create" on the listbox.
		# params - id of listbbox, ID of bitmap, size of bitmaps
		if self.bitmapMask is None:
			bitmapMask = RGB(0,0,255)
		else:
			bitmapMask = self.bitmapMask
		self.imageList = win32ui.CreateImageList(self.bitmapID, 16, 0, bitmapMask)
		if listControl is None:
			if self.listBoxId is None: self.listBoxId = win32ui.IDC_LIST1
			self.list = self._obj_ = parent.GetDlgItem(self.listBoxId)
		else:
			self.list = self._obj_ = listControl
			lbid = listControl.GetDlgCtrlID()
			assert self.listBoxId is None or self.listBoxId == lbid, "An invalid listbox control ID has been specified (specified as %s, but exists as %s)" % (self.listBoxId, lbid)
			self.listBoxId = lbid
		self.list.SetImageList(self.imageList, commctrl.LVSIL_NORMAL)
#		self.list.AttachObject(self)
		parent.HookNotify(self.OnTreeItemExpanding, commctrl.TVN_ITEMEXPANDING)
		parent.HookNotify(self.OnTreeItemSelChanged, commctrl.TVN_SELCHANGED)
		parent.HookNotify(self.OnTreeItemDoubleClick, commctrl.NM_DBLCLK)

		if self.root:
			self.AcceptRoot(self.root)

	def HierTerm(self):
		self.list.DeleteAllItems()
		self.root = None
		self.itemHandleMap = {}
		self.filledItemHandlesMap = {}
		parent = self.GetParentFrame()
		parent.HookNotify(None, commctrl.TVN_ITEMEXPANDING)
		parent.HookNotify(None, commctrl.TVN_SELCHANGED)
		parent.HookNotify(None, commctrl.NM_DBLCLK)
		self.list = None

	def OnTreeItemDoubleClick(self,(hwndFrom, idFrom, code), extra):
		if idFrom != self.listBoxId: return None
		item = self.itemHandleMap[self._obj_.GetSelectedItem()]
		self.TakeDefaultAction(item)
		return 1

	def OnTreeItemExpanding(self,(hwndFrom, idFrom, code), extra):
		if idFrom != self.listBoxId: return None
		action, itemOld, itemNew, pt = extra
		itemHandle = itemNew[0]
		if not self.filledItemHandlesMap.has_key(itemHandle):
			item = self.itemHandleMap[itemHandle]
			self.AddSubList(itemHandle, self.GetSubList(item))
			self.filledItemHandlesMap[itemHandle] = None
		return 0

	def OnTreeItemSelChanged(self,(hwndFrom, idFrom, code), extra):
		if idFrom != self.listBoxId: return None
		action, itemOld, itemNew, pt = extra
		itemHandle = itemNew[0]
		item = self.itemHandleMap[itemHandle]
		self.PerformItemSelected(item)
		return 1

	def AddSubList(self, parentHandle, subItems):
		for item in subItems:
			text = self.GetText(item)
#			hitem = self.list.InsertItem(text, 0, 1)
			if self.IsExpandable(item):
				cItems = 1 # Trick it !!
			else:
				cItems = 0
			bitmapCol = self.GetBitmapColumn(item)
			bitmapSel = self.GetSelectedBitmapColumn(item)
			if bitmapSel is None: bitmapSel = bitmapCol
			hitem = self.list.InsertItem(parentHandle, commctrl.TVI_LAST, (None, None, None, text, bitmapCol, bitmapSel, cItems, 0))
			self.itemHandleMap[hitem] = item
	
	def ItemFromHandle(self, handle):
		return self.itemHandleMap[handle]

	def AcceptRoot(self, root):
		self.list.DeleteAllItems()
		self.itemHandleMap = {}
		self.filledItemHandlesMap = {}
		subItems = self.GetSubList(root)
		self.AddSubList(0, subItems)

	def GetBitmapColumn(self, item):
		if self.IsExpandable(item):
			return 0
		else:
			return 4
	def GetSelectedBitmapColumn(self, item):
		return None # Use standard.

	def GetSelectedBitmapColumn(self, item):
		return 0

	def CheckChangedChildren(self):
		return self.list.CheckChangedChildren()
	def GetText(self,item):
		return GetItemText(item)
	def PerformItemSelected(self, item):
		try:
			win32ui.SetStatusText('Selected ' + self.GetText(item))
		except win32ui.error: # No status bar!
			pass
	def TakeDefaultAction(self, item):
		win32ui.MessageBox('Got item ' + self.GetText(item))

##########################################################################
#
# Classes for use with seperate HierListItems.
#
#
class HierListWithItems(HierList):
	def __init__(self, root, bitmapID = win32ui.IDB_HIERFOLDERS, listBoxID = None, bitmapMask = None): # used to create object.
		HierList.__init__(self, root, bitmapID, listBoxID, bitmapMask )
	def DelegateCall( self, fn):
		return fn()
	def GetBitmapColumn(self, item):
		rc = self.DelegateCall(item.GetBitmapColumn)
		if rc is None:
			rc = HierList.GetBitmapColumn(self, item)
		return rc
	def GetSelectedBitmapColumn(self, item):
		return self.DelegateCall(item.GetSelectedBitmapColumn)
	def IsExpandable(self, item):
		return self.DelegateCall( item.IsExpandable)
	def GetText(self, item):
		return self.DelegateCall( item.GetText )
	def GetSubList(self, item):
		return self.DelegateCall(item.GetSubList)
	def PerformItemSelected(self, item):
		func = getattr(item, "PerformItemSelected", None)
		if func is None:
			return HierList.PerformItemSelected( self, item )
		else:
			return self.DelegateCall(func)

	def TakeDefaultAction(self, item):
		func = getattr(item, "TakeDefaultAction", None)
		if func is None:
			return HierList.TakeDefaultAction( self, item )
		else:
			return self.DelegateCall(func)

# A hier list item - for use with a HierListWithItems
class HierListItem:
	def __init__(self):
		pass
	def GetText(self):
		pass
	def GetSubList(self):
		pass
	def IsExpandable(self):
		pass
	def GetBitmapColumn(self):
		return None	# indicate he should do it.
	def GetSelectedBitmapColumn(self):
		return None	# same as other
