# Database checker/fixer explained, more fixers
## Rationale
This add-on simultaneously solves three related problems.

### Meaningful error message
Sometime, Anki warns you that your database has trouble and that you 
should run «Check Database» to correct it. I find this quite 
frustrating, because I've no clue what's wrong. Since it may happen 
many times, I would like to understand what's wrong to avoid repeating 
the error. This is especially important for add-on developers, because 
if our add-ons break the database, it would be better to know exactly 
how it broke, so that we can correct this. Hence, this add-on changes 
messages sent by the methods used to check and to fix the database, so 
that they explain exactly what it does.

More information on the error messages can be found on
https://github.com/Arthur-Milchior/anki/blob/master/documentation/DB_Check.md

### Checking what Anki forgot to check
There are kinds of errors that Anki does not check. This add-on also 
checks and corrects those kinds of errors. The following error is 
currently considered:

* A note has two distinct cards for the same card type. If this is the
case, it keeps the card with the greatest interval. Ties are broken by
the one with greatest ease, then the one with the greatest due date,
then arbitrarily. I explain in [the
forum](https://anki.tenderapp.com/discussions/ankidesktop/32854-two-cards-of-the-same-note-with-same-nid#comment_47016398)
how this could occur without having a single add-on installed.
* Whether there are missing parameters in a deck (standard or
  dynamic/filtered), or deck option,
* Whether two notes have the same GUID. See
  https://github.com/Arthur-Milchior/anki-unique-GUID to understand
  why this may occur.


## Warning
This add-on is incompatible with add-on
* [12287769](https://ankiweb.net/shared/info/12287769) «Explain
deletion». This add-on ensures that the file `deleted.txt` states
why notes are deleted.
* [Quicker Anki: 802285486](https://ankiweb.net/shared/info/802285486)
  which makes some operations quicker.


Please instead use-addon
[777545149](https://ankiweb.net/shared/info/777545149) which merges
those three add-ons


With one exception, this add-on does not actually edit the
database. All editions are done by Anki original code. The exception
is the checks which are done by this add-on and not by Anki. Right
now, it's only: checking whether a note has a duplicate card.

## Internal
In the class `anki.collection._Collection`, it changes the
methods:
* `basicCheck`, a method used thrice during sync to check whether
everything is ok or whether there is an inconsistency.
* `fixIntegrity`, the method which is used when clicking on "Check
Database".
* `_checkFailed`. The new method explains the problem comes from
  the server.

## Version 2.0
None

## TODO
Use config to allow user to choose to have only one of the two
functionality. Allow to choose which card to keep.

Make it compatible with add-on mentioned above.

## Links, licence and credits

Key         |Value
------------|-------------------------------------------------------------------
Copyright   | Arthur Milchior <arthur@milchior.fr>
Based on    | Anki code by Damien Elmes <anki@ichi2.net>
License     | GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
Source in   | https://github.com/Arthur-Milchior/anki-database-check-explained
Addon number| [1135180054](https://ankiweb.net/shared/info/1135180054)
