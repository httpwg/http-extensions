---
title: Window Sizing for Zstandard Content Encoding
abbrev: Zstd Window Size
category: info

docname: draft-ietf-httpbis-zstd-window-size-latest
submissiontype: IETF
number:
date:
consensus: true
updates: 8878
v: 3
area: Web and Internet Transport
workgroup: HTTPBIS
keyword:
 - zstd
 - zstandard
 - compression
 - content encoding
 - content coding
 - application/zstd
venue:
  group: HTTP
  type: Working Group
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  github: httpwg/http-extensions/labels/zstd-window-size
  latest: "https://httpwg.org/http-extensions/draft-ietf-httpbis-zstd-window-size.html"
github-issue-label: zstd-window-size

author:
 -
    ins: N. Jaju
    fullname: Nidhi Jaju
    role: editor
    organization: Google
    street: Shibuya Stream, 3 Chome-21-3 Shibuya
    region: Shibuya City, Tokyo
    code: 150-0002
    country: Japan
    email: nidhijaju@google.com
 -
    ins: F. Handte
    fullname: W. Felix P. Handte
    role: editor
    organization: Meta Platforms, Inc.
    street: 380 W 33rd St
    city: New York
    region: NY
    code: 10001
    country: US
    email: felixh@meta.com

normative:

informative:


--- abstract

Deployments of Zstandard, or "zstd", can use different window sizes to limit
memory usage during compression and decompression. Some browsers and user
agents limit window sizes to mitigate memory usage concerns, causing
interoperability issues. This document updates the window size limit in RFC8878
from a recommendation to a requirement in HTTP contexts.


--- middle

# Introduction

Zstandard, or "zstd", specified in {{?RFC8878}}, is a lossless data compression
mechanism similar to gzip. When used with HTTP, the "zstd" content coding
token signals to the decoder that the content is Zstandard-compressed.

An important property of Zstandard-compressed content is its Window_Size
({{!RFC8878, Section 3.1.1.1.2}}), which describes the maximum distance for
back-references and therefore how much of the content must be kept in memory
during decompression.

The minimum Window_Size is 1 KB. The maximum Window_Size is
(1<<41) + 7*(1<<38) bytes, which is 3.75 TB. Larger Window_Size values tend
to improve the compression ratio, but at the cost of increased memory usage.

To protect against unreasonable memory usage, some browsers and user agents
limit the maximum Window_Size they will handle. This causes failures to decode
responses when the content is compressed with a larger Window_Size than the
recipient allows, leading to decreased interoperability.

{{!RFC8878, Section 3.1.1.1.2}} recommends that decoders support a Window_Size
of up to 8 MB, and that encoders not generate frames using a Window_Size larger
than 8 MB. However, it imposes no requirements.

This document updates {{RFC8878}} to enforce Window_Size limits on the encoder
and decoder for the "zstd" HTTP content coding.


# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Window Size

To ensure interoperability, when using the "zstd" content coding, decoders MUST
support a Window_Size of up to and including 8 MB, and encoders MUST NOT
generate frames requiring a Window_Size larger than 8 MB (see
{{zstd-iana-token}}).

# Security Considerations

This document introduces no new security considerations beyond those discussed
in {{RFC8878}}.

Note that decoders still need to take into account that they can receive
oversized frames that do not follow the window size limit specified in this
document and fail decoding when such invalid frames are received.

# IANA Considerations

## Content Encoding {#zstd-iana-token}

This document updates the entry added in {{RFC8878}} to the "HTTP Content
Coding Registry" within the "Hypertext Transfer Protocol (HTTP) Parameters"
registry:

Name:

: zstd

Description:

: A stream of bytes compressed using the Zstandard protocol with a Window_Size
  of not more than 8 MB.

Reference:

: This document and {{RFC8878}}


--- back

# Acknowledgments
{:numbered="false"}

Zstandard was developed by Yann Collet.

The authors would like to thank Yann Collet, Klaus Post, Adam Rice, and members
of the Web Performance Working Group in the W3C for collaborating on the window
size issue and helping to formulate a solution. Also, thank you to Nick Terrell
for providing feedback that went into RFC 8478 and RFC 8878.

