// printer info class
class PYW_EXPORT ui_prinfo_object : public ui_assoc_object {
protected:
  ui_prinfo_object() : m_deletePrInfo (FALSE) { }
  ~ui_prinfo_object();
  virtual void SetAssocInvalid();
  virtual void DoKillAssoc( BOOL bDestructing = FALSE );
public:
  static ui_type type;
  MAKE_PY_CTOR(ui_prinfo_object)
  static CPrintInfo *GetPrintInfo(PyObject *self);
  BOOL m_deletePrInfo;
};
