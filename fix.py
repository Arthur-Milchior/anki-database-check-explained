from anki.collection import _Collection
from anki.consts import *
from anki.lang import _, ngettext
from aqt import mw

def integrity(self):
    if self.db.scalar("pragma integrity_check") != "ok":
        return (_("The database containing the collection is corrupt (i.e. pragma integrity_check fails). Please see the manual."), False)

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
# def noteWithMissingModel(self, problems):
#     l = self.db.all("""select id, flds, tags, mid from notes where mid not in """ + ids2str(self.models.ids()))
#     for id, flds, tags, mid in l:
#         problems.append(f"Deleted note {id}, with fields «{filds}», tags «{tags}» whose model id is {mid}, which does not exists.")
#     if l:
#          problems.appends(ngettext("Deleted %d note with missing note type.",
#                                    "Deleted %d notes with missing note type.", len(l))
#                           % len(l))
#          self.remNotes([tup[0] for tup in l])

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

def fixInvalidCardOrdinal(self, problems):
    for m in self.models.all():
        if m['type'] == MODEL_STD:
            # cards with invalid ordinal
            l = self.db.all("""
            select id, ord, nid from cards where (ord <0 or ord >= %d) and nid in (
select id from notes where mid = ?)""" %
                               len(m['tmpls']),
                               m['id'])
            for id, ord, nid in l:
                problems.append("Deleted card {id} of note {nid} because its {ord} does not belong to its model")
            if l:
                problems.append(
                    ngettext("Deleted %d card with missing template.",
                             "Deleted %d cards with missing template.",
                             len(l)) % len(l))
                self.remCards([tup[0] for tup in l])

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

def fixNoteWithoutCard(self, problems):
    l = self.db.all("""select id, flds, tags, mid from notes where id not in (select distinct nid from cards)""")
    for id, flds, tags, mid in l:
        problems.append("Deleting note {id} with fields «{flds}» and tags «{tags}» of model {mid} because it has no card.")
    if l:
        cnt = len(l)
        problems.append(
            ngettext("Deleted %d note with no cards.",
                     "Deleted %d notes with no cards.", cnt) % cnt)
        self._remNotes([tup[0] for tup in l])

def fixCardWithoutNote(self,problems)
    l = self.db.all("""select id, nid from cards where nid not in (select id from notes)""")
    for id, nid in l:
        problems.append(f"Deleted card {id} of note {nid} because this note does not exists.")
    if l:
        cnt = len(l)
        problems.append(
            ngettext("Deleted %d card with missing note.",
                     "Deleted %d cards with missing note.", cnt) % cnt)
        self.remCards([tup[0] for tup in l])

def fixOdue(self, problems):
    ids = self.db.all("""
select id from cards where odue > 0 and (type=1 or queue=2) and not odid""")
    if ids:
        cnt = len(ids)
        problems.append(
            ngettext("Fixed %d card with invalid properties.",
                     "Fixed %d cards with invalid properties.", cnt) % cnt)
        self.db.execute("update cards set odue=0 where id in "+
            ids2str(ids))


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
                fixOdue]:
        fun(self,problems)



    # cards with odid set when not in a dyn deck
    dids = [id for id in self.decks.allIds() if not self.decks.isDyn(id)]
    ids = self.db.all("""
select id from cards where odid > 0 and did in %s""" % ids2str(dids))
    if ids:
        cnt = len(ids)
        problems.append(
            ngettext("Fixed %d card with invalid properties.",
                     "Fixed %d cards with invalid properties.", cnt) % cnt)
        self.db.execute("update cards set odid=0, odue=0 where id in "+
            ids2str(ids))
    # tags
    self.tags.registerNotes()
    # field cache
    for m in self.models.all():
        self.updateFieldCache(self.models.nids(m))
    # new cards can't have a due position > 32 bits
    self.db.execute("""
update cards set due = 1000000, mod = ?, usn = ? where due > 1000000
and type = 0""", intTime(), self.usn())
    # new card position
    self.conf['nextPos'] = self.db.scalar(
        "select max(due)+1 from cards where type = 0") or 0
    # reviews should have a reasonable due #
    ids = self.db.all(
        "select id from cards where queue = 2 and due > 100000")
    if ids:
        problems.append("Reviews had incorrect due date.")
        self.db.execute(
            "update cards set due = ?, ivl = 1, mod = ?, usn = ? where id in %s"
            % ids2str(ids), self.sched.today, intTime(), self.usn())
    # v2 sched had a bug that could create decimal intervals
    curs = self.db.cursor()
     curs.execute("update cards set ivl=round(ivl),due=round(due) where ivl!=round(ivl) or due!=round(due)")
    if curs.rowcount:
        problems.append("Fixed %d cards with v2 scheduler bug." % curs.rowcount)

    curs.execute("update revlog set ivl=round(ivl),lastIvl=round(lastIvl) where ivl!=round(ivl) or lastIvl!=round(lastIvl)")
    if curs.rowcount:
        problems.append("Fixed %d review history entries with v2 scheduler bug." % curs.rowcount)
    # and finally, optimize
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
