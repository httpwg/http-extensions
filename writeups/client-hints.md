# Shepherd Writeup for draft-ietf-httpbis-client-hints

## 1. Summary

Mark Nottingham is the Document Shepherd; Barry Lieba is the Responsible AD.

An increasing diversity of Web-connected devices and software capabilities has created a need to deliver optimized content for each device.

This specification defines a set of HTTP request header fields, colloquially known as Client Hints, to address this. They are intended to be used as input to proactive content negotiation; just as the Accept header field allows clients to indicate what formats they prefer, Client Hints allow clients to indicate a list of device and agent specific preferences.

The intended status is Experimental, as there is currently only implementation in one major browser engine (Chromium, used in several browsers). The Working Group felt that it was useful to document this protocol extension to improve interoperability and encourage further implementation.

## 2. Review and Consensus

The document was reviewed by a broad range of Working Group participants, as well as external parties (through Github and other external venues). Members of the Web performance optimisation community are especially interested in this specification, as it allows for automating the use of "responsive images."

Consensus is rough regarding how useful this specification will be, but there was agreement that it was useful to document; hence the Experimental status.

## 3. Intellectual Property

The authors confirm that to their direct, personal knowledge, all IPR related to this document has already been disclosed.


## 4. Other Points

There are no downrefs.  IANA Considerations are clear.

