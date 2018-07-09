# Shepherd Writeup for draft-ietf-httpbis-expect-ct

## 1. Summary

Mark Nottingham is the document shepherd. Alexey Melnikov is the responsible Area Director.

This document defines a new HTTP header field, named Expect-CT, that allows web host operators to
instruct user agents to expect valid Signed Certificate Timestamps (SCTs) to be served on
connections to these hosts. Expect-CT allows web host operators to discover misconfigurations in
their Certificate Transparency deployments and ensure that misissued certificates accepted by UAs
are discoverable in Certificate Transparency logs.

## 2. Review and Consensus

This document did not see a tremendous amount of discussion after the Working Group agreed to adopt it, but did see a number of reviews from within the community. Given its intended status as Experimental, we believe this is appropriate.

## 3. Intellectual Property

The author has confirmed that to her direct, personal knowledge, all IPR related to this document has already been disclosed.

## 4. Other Points

The IANA considerations seem correct, except that the requested registry needs to be more specific - it will be a permanent registration. This will be corrected in the next revision (currently the submission queue is closed).
