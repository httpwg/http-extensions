# Shepherd Writeup for draft-ietf-httpbis-encryption-encoding

## 1. Summary

Mark Nottingham is the document shepherd; Alexey Melnikov is the responsible Area Director.

This memo introduces a content-coding for HTTP that allows message payloads to
be encrypted.

The intended status is Proposed Standard.

## 2. Review and Consensus

This document has been discussed for some time in the Working Group, going through several
revisions and reviews. The editor is primarily responsible for the design, but reviews by a number
of other people have shaped its design over time.

The most immediate use case comes from the WEBPUSH WG. 

A list of implementations can be found at:
  https://github.com/httpwg/wiki/wiki/EncryptedContentEncoding
Note that some need to be updated to reflect the latest draft.

## 3. Intellectual Property

Martin has confirmed that, to his direct, personal knowledge, all IPR related to this document has
already been disclosed, in conformance with BCPs 78 and 79.

One IPR disclosure has been made for this document; see <https://datatracker.ietf.org/ipr/2777/>.
The Working Group was informed of this (see
<http://www.w3.org/mid/36BF957B-31D7-4F47-8C80-4F0506D09E64@mnot.net>), but no changes to the draft
resulted.

## 4. Other Points

This document has a downward reference to RFC5869, which is already in the DOWNREF Registry.
