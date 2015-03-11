# Shepherd Writeup for auth-info

## 1. Summary

The document shepherd is Mark Nottingham; the responsible Area Director is Barry Leiba.

This specification defines the "Authentication-Info" and "Proxy-Authentication-Info" response header fields for use in HTTP authentication schemes which need to return information once the client's authentication credentials have been accepted.


## 2. Review and Consensus

This document separates the definition of the "Authentication-Info" and "Proxy-Authentication-Info" HTTP header fields from RFC2617, so that they can be used by other HTTP authentication schemes (including some being actively developed).

As such, the header fields have already enjoyed implementation and deployment; we have merely re-specified them for more generic use. Because other Working Groups depend upon this specification to progress their work items, we have done this work fairly quickly, but with care.

The resulting specification has been reviewed by several Working Group members, and after a small amount of discussion, its content has been uncontroversial.


## 3. Intellectual Property

Julian Reschke has confirmed that any IPR he's personally aware of related to this document has been disclosed. No other discussion of related IPR has taken place.


## 4. Other Points

The document does not contain any downreferences.

This document updates the IANA Message Headers registry, and contains clear instructions. It does not establish any new registries.
