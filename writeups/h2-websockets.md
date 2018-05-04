# Shepherd Writeup for draft-ietf-httpbis-h2-websockets

## 1. Summary

Mark Nottingham is the Document Shepherd; Alexey Melnikov is the responsible Area Director.

This document defines a mechanism for running the WebSocket Protocol over a single stream of an
HTTP/2 connection.

The intended publication type is Proposed Standard.

## 2. Review and Consensus

This document enjoyed broad discussion and review in the HTTP Working Group; there seems to be
significant community interest in it, since it enables the use of WebSockets on a HTTP/2 server,
reducing operational issues for Web sites.

Deployment depends upon implementation in Web browsers; at least one has already written code for
this feature and is in process of shipping it.

There was some concern about whether it was appropriate for a version-specific extension (a HTTP/2
SETTING) to modify the semantics of a version-generic HTTP method (CONNECT), but the WG reached
consensus that CONNECT is "special" in this regard.

## 3. Intellectual Property

[ Confirm that each author has stated that their direct, personal knowledge of any IPR related to this document has already been disclosed, in conformance with BCPs 78 and 79. Explain briefly the working group discussion about any IPR disclosures regarding this document, and summarize the outcome. ]

## 4. Other Points

The document does not have any downrefs.

IDNits points out some minor issues which will be addressed in a subsequent draft.

The IANA Considerations are concise and correct. Note that 0x8 was chosen to avoid colliding with
draft-ietf-httpbis-cache-digest.
