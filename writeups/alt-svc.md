# Shepherd Writeup for Alt-Svc

## 1. Summary

Mike Bishop is the document shepherd; Barry Leiba is the responsible 
Area Director. 

This document specifies a method to provide clients authoritative access 
to HTTP origins at a different network location and/or using a different 
protocol stack. 

The requested publication type is Proposed Standard. 

## 2. Review and Consensus 

The document started as an individual draft which provided a potential 
solution to several related problems in the HTTP space, helping clients 
become aware of multiple network or protocol endpoints for an origin 
that could serve the same content in different ways. It drew inspiration 
from an existing proprietary solution, Alternate-Protocol, used by 
Chromium during SPDY development. 

There was implementation interest from Mozilla Firefox and Akamai, along 
with willingness from Google Chrome to migrate from Alternate-Protocol 
to Alt-Svc. Other implementers were less interested, but as the behavior 
is fully optional for clients, the consensus was to adopt the document. 
During the HTTP/2 standardization process, the Alt-Svc document was 
discussed and worked on in parallel; HTTP/2-specific pieces were 
originally added to the HTTP/2 specification at the time of adoption, 
but were moved into this document after HTTP/2's extension story was 
agreed upon. 

There has been some interest in defining additional ways to discover 
Alternative Services, and this document intentionally does not close the 
door on that. It discusses client behavior when dealing with 
Alternatives of which it is aware, and defines two possible ways a 
client can learn about Alternatives. Future drafts may define additional 
ways, such as DNS. 

Technical discussions involved a broad section of the working group, 
with the most focus from a few client and proxy implementers. There has 
been some back and forth about the right balance between utility and 
security, but the document now reflects general consensus. This is 
reflected by a thoroughly-discussed Security Considerations section, 
which covers ways in which Alt-Svc could be used to track clients or 
persist attacks, and gives guidance to implementations on ways to 
minimize the potential impacts.

## 3. Intellectual Property 

Each author has stated that their direct, personal knowledge of any IPR 
related to this document has already been disclosed, in conformance with 
BCPs 78 and 79.

No disclosures have been submitted regarding prior work in this space.

## 4. Other Points 

There are no downward references. The IANA Considerations are clear, and 
the Expert Reviewers for the existing registries have been actively 
involved in the draft process. A new registry is also created for 
parameters modifying properties of Alt-Svc listings.

There was some discussion over whether parameters would be 
mandatory-to-understand (ignoring the entire entry otherwise), or always 
optional. In the end, parameters were made optional-to-understand in all 
cases, to avoid exploding the list of alternatives when multiple 
optional parameters were used.

