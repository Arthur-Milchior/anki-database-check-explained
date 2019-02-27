from anki.collection import _Collection
from anki.consts import *
from anki.lang import _, ngettext
from aqt import mw

def integrity(self):
    if self.db.scalar("pragma integrity_check") != "ok":
        return (_("The database containing the collection is corrupt (i.e. pragma integrity_check fails). Please see the manual."), False)

def fixOverride(self, problems):
    for m in self.models.all():
        for t in m['tmpls']:
            if t['did'] == "None":
                t['did'] = None
                problems.append(_("Fixed AnkiDroid deck override bug. (I.e. some template has did = to 'None', it is now None.)"))
                self.models.save(m)

def fixMissingReq(self, problems):
    for m in self.models.all():
        if m['type'] == MODEL_STD:
            # model with missing req specification
            if 'req' not in m:
                self.models._updateRequired(m)
                problems.append(_("Fixed note type %s whose 'req' was missing.") % m['name'])

def template(query, problem, singular, plural, action):
    def f(self,problems):
        l = self.db.all(query)
        for tup in l:
            problems.append(problem.format(*tup))
        if l:
             problems.appends(ngettext(singular,
                                       plural, len(l))
                              % len(l))
             action([tup[0] for tup in l])
    return f

noteWithMissingModel = template(
    """select id, flds, tags, mid from notes where mid not in """ + ids2str(self.models.ids()),
    "Deleted note {}, with fields «{}», tags «{}» whose model id is {}, which does not exists.",
    "Deleted %d note with missing note type.",
    "Deleted %d notes with missing note type.",
    mw.col.remNotes

)

def fixInvalidCardOrdinal(self, problems):
    funs = [
        template(
            f"""select id, nid, ord from cards where (ord <0 or ord >= {len(m['tmpls'])}) and nid in (select id from notes where mid = {m['id']})""",
            "Deleted card {} of note {} because its {} does not belong to its model",
            "Deleted %d card with missing template.",
            "Deleted %d cards with missing template.",
            mw.col.remCards)
        for m in mw.col.models.all()]
    for fun in funs:
        fun(self,problems)

def fixWrongNumberOfField(self, problems):
    for m in self.models.all():
        # notes with invalid field count
        l = self.db.execute(
            "select id, flds, mid from notes where mid = ?", m['id'])
        for id, flds, mid in l:
            if (flds.count("\x1f") + 1) != len(m['flds']):
                ids.append(id)
                problems.append(f"""Note {nid} with fields «{flds}» has {flds.count("\x1f") + 1} fields while its model {m['name']} has {len(m['flds'])} fields""")
        if l:
            problems.append(
                ngettext("Deleted %d note with wrong field count.",
                         "Deleted %d notes with wrong field count.",
                         len(ids)) % len(ids))
            self.remNotes([tup[0] for tup in l])

fixNoteWithoutCard = template(
    """select id, flds, tags, mid from notes where id not in (select distinct nid from cards)""",
    "Deleting note {} with fields «{}» and tags «{}» of model {} because it has no card.",
    "Deleted %d note with no cards.",
    "Deleted %d notes with no cards.",
    mw.col._remNotes
    )

fixCardWithoutNote = template(
    "select id, nid from cards where nid not in (select id from notes)",
    "Deleted card {} of note {} because this note does not exists.",
    "Deleted %d card with missing note.",
    "Deleted %d cards with missing note.",
    mw.col.remCards)

def odueToZero(ids):
    mw.col.db.execute("update cards set odue=0 where id in "+
                      ids2str(ids))
fixOdueType1 = template(
    "select id,nid from cards where odue > 0 and type=1 and not odid",
    "set odue of card {} of note {} to 0, because it was positive while type was 1 (i.e. card in learning)"
    "Fixed %d card with invalid properties.",
    "Fixed %d cards with invalid properties.",
    odueToZero))

fixOdueQueue2 = template(
    "select id, nid from cards where odue > 0 and queue=2 and not odid",
    "set odue of card {} of note {} to 0, because it was positive while queue was 2 (i.e. in the review queue)."
    "Fixed %d card with invalid properties.",
    "Fixed %d cards with invalid properties.",
    odueToZero)

fixOdidOdue = template(
    """select id, odid, did from cards where odid > 0 and did in %s""" % ids2str([id for id in self.decks.allIds() if not self.decks.isDyn(id)]),# cards with odid set when not in a dyn deck
    "Card {}: Set odid and odue to 0 because odid was {} while its did was {} which is not filtered(a.k.a. not dymanic).",
    "Fixed %d card with invalid properties.",
    "Fixed %d cards with invalid properties.",
    (lambda ids:mw.col.db.execute("update cards set odid=0, odue=0 where id in "+
            ids2str(ids))))

def atMost1000000Due(self):
    # new cards can't have a due position > 32 bits
    self.db.execute("""
update cards set due = 1000000, mod = ?, usn = ? where due > 1000000
and type = 0""", intTime(), self.usn())

def setNextPos(self):
    # new card position
    self.conf['nextPos'] = self.db.scalar(
        "select max(due)+1 from cards where type = 0") or 0

reasonableRevueDue = template(# reviews should have a reasonable due #
    "select id, due from cards where queue = 2 and due > 100000",
    "Changue  of card {}, because its due is {} which is excessive",
    "Reviews had incorrect due date.",
    "Reviews had incorrect due date.",
    (lambda ids:mw.col.db.execute(
        "update cards set due = ?, ivl = 1, mod = ?, usn = ? where id in %s"
        % ids2str(ids), mw.col.sched.today, intTime(), mw.col.usn()))
    )

# v2 sched had a bug that could create decimal intervals
fixFloatIvl = template(
    "select id, ivl from cards where ivl != round(ivl)",
    "Round the ivl of card {id} because it was {ivl} (this is a known bug of schedule v2.",
    "Fixed %d cards with v2 scheduler bug.",
    "Fixed %d cards with v2 scheduler bug.",
    (lambda ids:
     "update cards set ivl = round(ivl) where id in "+ids(ids))
)
fixFloatDue = template(
    "select id, due from cards where due != round(due)",
    "Round the due of card {id} because it was {due} (this is a known bug of schedule v2.",
    "Fixed %d cards with v2 scheduler bug.",
    "Fixed %d cards with v2 scheduler bug.",
    (lambda ids:
     "update cards set due = round(due) where id in "+ids(ids))
)

def fixIntegrity(self):
    "Fix possible problems and rebuild caches."
    problems = []
    self.save()
    oldSize = os.stat(self.path)[stat.ST_SIZE]

    ret = integrity(self):
    if ret:
        return ret

    for fun in [noteWithMissingModel,
                fixOverride,
                fixMissingReq,
                fixInvalidCardOrdinal,
                fixWrongNumberOfField,
                fixNoteWithoutCard,
                fixCardWithoutNote,
                fixOdueType1,
                fixOdueQueue2,
                fixOdidOdue,
                reasonableRevueDue,
                fixFloatIvl,
                fixFloatDue,
    ]:
        fun(self,problems)
    # tags
    self.tags.registerNotes()
    # field cache
    for m in self.models.all():
        self.updateFieldCache(self.models.nids(m))
    atMost1000000Due(self),
    setNextPos(self)

    self.optimize()
    newSize = os.stat(self.path)[stat.ST_SIZE]
    txt = _("Database rebuilt and optimized.")
    ok = not problems
    problems.append(txt)
    # if any problems were found, force a full sync
    if not ok:
        self.modSchema(check=False)
    self.save()
    return ("\n".join(problems), ok)

_Collection.fixIntegrity
