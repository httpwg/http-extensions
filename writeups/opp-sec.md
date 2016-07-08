# Shepherd Writeup for HTTP Opportunistic Security

## 1. Summary

Mike Bishop is the document shepherd; Alexey Melnikov is the responsible 
Area Director. 

This document presents an experimental way to use 
[Alt-Svc](https://tools.ietf.org/html/rfc7838) to achieve opportunistic 
encryption connections to http:// schemed resources. While this does not 
offer the true security guarantees of the https:// scheme, it does 
improve resistance to passive surveillance by requiring some minimal 
level of active attack to defeat. 

## 2. Review and Consensus

The document has been closely reviewed and discussed by a small number 
of vocal participants, with a larger number of other participants adding 
occasional feedback. The community is generally divided about the 
utility of providing a tool which is so easily defeated by an active 
attacker, but there have been very few who believe this experiment would 
be detrimental. The primary concern voiced by dissenters has been that 
widespread deployment might provide a false sense of security, slowing 
the adoption of "real" HTTPS or confusing users. The restriction in 
section 8.1 was added to help mitigate this concern.

RFC 7838 requires "reasonable assurances" that the alternative was under 
the control of the same authority as the origin. RFC 7838 defines only 
one means of having such assurance: possession of a TLS certificate for 
the origin. A second method originally in that document, being a 
different port on the same host, was controversial and was moved into 
this experimental draft for further discussion. The concern was that 
attacker-controlled content in concert with an attacker-owned process 
running on an arbitrary port could hijack control of other resources on 
the origin. This draft adds additional logic using a resource at a 
[.well-known URI](https://tools.ietf.org/html/rfc5785) which would be 
more difficult for an attacker to control. This is believed to be a 
sufficient mitigation, and the refinement of this resource has been the 
focus of most of the last-call feedback.

That well-known resource also contains the ability for an HTTP origin to 
"commit" to always having an authenticated, encrypted alternative 
service available. Clients which respect this commitment would fail to 
connect when encryption cannot be established, rather than being 
vulnerable to a downgrade attack. This is a weaker analog to HSTS, since 
the resource remains in the http:// namespace with associated lessened 
security properties in most clients. This offers some mitigation against 
active attackers after the first connection. 

There is a client implementation in Mozilla Firefox, though other 
browsers have expressed limited interest at this time. No explicit 
implementation of this draft is required in server software (the 
necessary resources and headers can be administratively configured), but 
one concern which has been raised is the more general support of server 
software for receiving requests for http:// schemed resources on ports 
configured to use TLS. While HTTP/1.1 permits and HTTP/2 mandates the 
inclusion of the URL scheme with the request, it appears that almost no 
server implementations treat the request as more authoritative than the 
port on which it was received. This is noted in section 8.4. A primary 
learning from experimentation with this draft will be to what degree 
this server behavior presents a deployment issue in the real world. 

## 3. Intellectual Property

Each author has stated that their direct, personal knowledge of any IPR 
related to this document has already been disclosed, in conformance with 
BCPs 78 and 79. No IPR disclosures have been submitted regarding this 
document. 

## 4. Other Points

There are no downward references. The IANA Considerations are clear, and 
the Expert Reviewer for the affected registry is an author of this draft.