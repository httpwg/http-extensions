# Shepherd Writeup for draft-ietf-httpbis-cice

## 1. Summary

Mark Nottingham is the document shepherd; Barry Leiba is the responsible Area Director.

In HTTP, content codings allow for payload encodings such as for compression or integrity checks. In particular, the "gzip" content coding is widely used for payload data sent in response messages.

Content codings can be used in request messages as well, however discoverability is not on par with response messages. This document extends the HTTP "Accept-Encoding" header field for use in responses, to indicate that content codings are supported in requests.

## 2. Review and Consensus

This document was discussed at a few meetings, as well as on the list. It was reviewed by a number of people, and a few different designs were discussed early in its lifetime before we settled on the current design. 

There is not currently any known implementation; this document is "filling a hole" in HTTP, and we
have seem some interest from implementers and deployers of HTTP.

## 3. Intellectual Property

Julian has confirmed that to his direct, personal knowledge, there is no IPR related to this document.

## 4. Other Points

This document does not contain any downreferences, and its IANA considerations are clear. 
