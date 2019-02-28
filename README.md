# Database checker/fixer explained, more fixers
__WARNING__ : This add-on is still in beta mode. It is supposed to
_Fix_ the database. However, as anything updating the database, it may
actually hurt it if there is a bug not yet found. Hence, be sure to
have a backup of your collection before running «check media».

## Rationale
This add-on simultaneously solve two related problems.

### Meaningful error message
Sometime, anki warns you that your database has trouble. That you
should run «Check database» to correct it. I find this quite
frustrating, because I've no clue what's wrong. And since it may
happens many time, I would like to understand what's wrong to avoid
repeating the error. This is especially important for add-on
developpers, because if our add-ons break the database, it would be
better to know exactly how it breaks, so that we can correct
this. Hence, this add-on change message sent by the methods used to
check and to fix the database, so that it explains exactly what it
does.

### Checking what anki forgot to check
There are kind(s) of error(s) that anki does not check. This add-on
also check and correct those kind of errors. The following error(s)
are currently considered:
* Whether you have a note which has two distinct cards for the same
card type. If this is the case, it keeps the card with greatest
interval. In case of equality, it keeps the one with greatest
easyness. In case of equality the one with greates due
date. Otherwise, an arbitrary card.


## Warning
This add-on is incompatible with add-on
[12287769](https://ankiweb.net/shared/info/12287769) «Explain
deletion». This add-on ensure that the file ```deleted.txt``` state
why notes are deleted.

## Internal
In the class ```anki.collection._Collection```, it changes the two
methods ```basicCheck``` and ```fixIntegrity```.

## Version 2.0
None

## TODO
Use config to allow user to choose to have only one of the two
functionnality. Allow to choose which card to keep.

Make it compatible with add-on mentionned above.

## Links, licence and credits

Key         |Value
------------|-------------------------------------------------------------------
Copyright   | Arthur Milchior <arthur@milchior.fr>
Based on    | Anki code by Damien Elmes <anki@ichi2.net>
License     | GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
Source in   | https://github.com/Arthur-Milchior/anki-database-check-explained
Addon number| [1135180054](https://ankiweb.net/shared/info/1135180054)
