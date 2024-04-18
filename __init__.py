"""
Update History:
* Sun Apr 14 2024 Mike Heitmann, N0SO <n0so@arrl.net>
- V0.0.1 - First interation
* Mon Apr 15 2024 Mike Heitmann, N0SO <n0so@arrl.net>
- V0.0.2 - Tweaked format of "WORKEDBY" data. Replaced comma with
-          a space character (W0MA,K0GQ... to W0MA K0GQ... The commas
-          were preventing a line wrap in the HTML report.
* Thu Apr 18 2024 Mike Heitmann, N0SO <n0so@arrl.net>
- V0.1.0 - Added code to lookup orphan calls on QRZ.COM. This adds
-          significantly to the processing time if --createTable is
-          True, so also added a --dontLookupCalls option to skip the
-          QRZ lookup. The database fields get filled in to the lookup
-          can happen later. Need to update code to add the QRZ data
-          in place without re-creating the entire table.
"""
VERSION = '0.1.0' 

