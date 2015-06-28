# Shepherd Writeup for draft-ietf-httpbis-tunnel-protocol

## 1. Summary

Mark Nottingham is the document shepherd; Barry Leiba is the responsible Area Director.

This specification allows HTTP CONNECT requests to indicate what protocol will be used within the tunnel once established, using the ALPN header field.

Its intended status is Proposed Standard.

## 2. Review and Consensus

This document was brought to the Working Group as a result of work in WebRTC and related groups, 
to satisfy a requirement there.

It was discussed in WG meetings as well as on-list, with a broad selection of participants. 

Some participants were concerned that the mechanism is not verifiable; i.e., an intermediary does not have any assurance that the protocol in use inside an encrypted tunnel is actually advertised. However, we found that this is acceptable, because of the nature of the mechanism; it is not designed to provide such assurances, but instead allow coordination between cooperating (or semi-cooperating) actors.

Other participants were concerned because of confusion about whether this mechanism can be used when TLS is not in use, and the ambiguity that the use of ALPN entails when it is not. We resolved this by explicitly linking it to ALPN, so that the protocol identifier can nominate whether encryption is in use.

To our knowledge, this specification has not been implemented yet. This is not surprising, given the nature of the extension. 


## 3. Intellectual Property

Each author has stated that their direct, personal knowledge of any IPR related to this document has already been disclosed. 

No IPR declarations have been made.


## 4. Other Points

Idnits reports a few problems, but they are spurious.

IANA Considerations does not precisely identify the registry being entered into; the next draft will correct this.
