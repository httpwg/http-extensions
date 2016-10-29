---
title: Encrypted Content-Encoding for HTTP
abbrev: HTTP encryption coding
docname: draft-ietf-httpbis-encryption-encoding-latest
date: 2016
category: std

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Internet-Draft

stand_alone: yes
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline, docmapping]

author:
 -
    ins: M. Thomson
    name: Martin Thomson
    organization: Mozilla
    email: martin.thomson@gmail.com

normative:
  FIPS180-4:
    title: NIST FIPS 180-4, Secure Hash Standard
    author:
      name: NIST
      ins: National Institute of Standards and Technology, U.S. Department of Commerce
    date: 2012-03
    target: http://csrc.nist.gov/publications/fips/fips180-4/fips-180-4.pdf

informative:
  XMLENC:
    title: "XML Encryption Syntax and Processing"
    author:
      - ins: D. Eastlake
      - ins: J. Reagle
      - ins: F. Hirsch
      - ins: T. Roessler
      - ins: T. Imamura
      - ins: B. Dillaway
      - ins: E. Simon
      - ins: K. Yiu
      - ins: M. Nyström
    date: 2013-01-24
    seriesinfo: W3C Recommendation REC-xmlenc-core1-20130411
    target: "https://www.w3.org/TR/2013/REC-xmlenc-core1-20130411"
  AEBounds:
    title: "Limits on Authenticated Encryption Use in TLS"
    author:
      - ins: A. Luykx
      - ins: K. Paterson
    date: 2016-03-08
    target: "http://www.isg.rhul.ac.uk/~kp/TLS-AEbounds.pdf"

--- abstract

This memo introduces a content coding for HTTP that allows message payloads to
be encrypted.

--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/encryption>.

--- middle

# Introduction

It is sometimes desirable to encrypt the contents of a HTTP message (request or
response) so that when the payload is stored (e.g., with a HTTP PUT), only
someone with the appropriate key can read it.

For example, it might be necessary to store a file on a server without exposing
its contents to that server. Furthermore, that same file could be replicated to
other servers (to make it more resistant to server or network failure),
downloaded by clients (to make it available offline), etc.  without exposing its
contents.

These uses are not met by the use of TLS {{?RFC5246}}, since it only encrypts
the channel between the client and server.

This document specifies a content coding (Section 3.1.2 of {{!RFC7231}}) for HTTP
to serve these and other use cases.

This content coding is not a direct adaptation of message-based encryption
formats - such as those that are described by {{?RFC4880}}, {{?RFC5652}},
{{?RFC7516}}, and {{XMLENC}} - which are not suited to stream processing, which
is necessary for HTTP.  The format described here cleaves more closely to the
lower level constructs described in {{!RFC5116}}.

To the extent that message-based encryption formats use the same primitives, the
format can be considered as sequence of encrypted messages with a particular
profile.  For instance, {{jwe}} explains how the format is congruent with a
sequence of JSON Web Encryption {{?RFC7516}} values with a fixed header.

This mechanism is likely only a small part of a larger design that uses content
encryption.  How clients and servers acquire and identify keys will depend on
the use case.  Though a complete key management system is not described, this
document defines an Crypto-Key header field that can be used to convey keying
material.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in {{!RFC2119}}.

Base64url encoding is defined in Section 2 of {{!RFC7515}}.


# The "aes128gcm" HTTP Content Coding {#aesgcm}

The "aes128gcm" HTTP content coding indicates that a payload has been encrypted
using Advanced Encryption Standard (AES) in Galois/Counter Mode (GCM) as
identified as AEAD_AES_128_GCM in {{!RFC5116}}, Section 5.1.  The AEAD_AES_128_GCM
algorithm uses a 128 bit content encryption key.

When this content coding is in use, the Encryption header field ({{encryption}})
describes how encryption has been applied.  The Crypto-Key header field
({{crypto-key}}) can be included to describe how the content encryption key is
derived or retrieved.

The "aes128gcm" content coding uses a single fixed set of encryption
primitives.  Cipher suite agility is achieved by defining a new content coding
scheme.  This ensures that only the HTTP Accept-Encoding header field is
necessary to negotiate the use of encryption.

The "aes128gcm" content coding uses a fixed record size.  The final encoding
consists of a header (see {{header}}), zero or more fixed size encrypted records
and a partial record.  The partial record MUST be shorter than the fixed record
size.

~~~ drawing
      +-----------+       content is rs octets minus padding
      |   data    |       of between 2 and 65537 octets;
      +-----------+       the last record is smaller
           |
           v
+-----+-----------+       add padding to get rs octets;
| pad |   data    |       the last record contains
+-----+-----------+       up to rs minus 1 octets
         |
         v
+--------------------+    encrypt with AEAD_AES_128_GCM;
|    ciphertext      |    final size is rs plus 16 octets
+--------------------+    the last record is smaller
~~~

The record size determines the length of each portion of plaintext that is
enciphered, with the exception of the final record, which is necessarily
smaller.  The record size ("rs") is included in the content coding header (see
{{header}}).

AEAD_AES_128_GCM produces ciphertext 16 octets longer than its input plaintext.
Therefore, the length of each enciphered record other than the last is equal to
the value of the "rs" parameter plus 16 octets.  To prevent an attacker from
truncating a stream, an encoder MUST append a record that contains only padding
and is smaller than the full record size if the final record ends on a record
boundary.  A receiver MUST fail to decrypt if the final record ciphertext is
less than 18 octets in size or equal to the record size plus 16 (that is, the
size of a full encrypted record).  Valid records always contain at least two
octets of padding and a 16 octet authentication tag.

Each record contains between 2 and 65537 octets of padding, inserted into a
record before the enciphered content. Padding consists of a two octet unsigned
integer in network byte order, followed that number of zero-valued octets. A
receiver MUST fail to decrypt if any padding octet other than the first two are
non-zero, or a record has more padding than the record size can accommodate.

The nonce for each record is a 96-bit value constructed from the record sequence
number and the input keying material.  Nonce derivation is covered in {{nonce}}.

The additional data passed to each invocation of AEAD_AES_128_GCM is a
zero-length octet sequence.

A consequence of this record structure is that range requests {{?RFC7233}} and
random access to encrypted payload bodies are possible at the granularity of the
record size.  Partial records at the ends of a range cannot be decrypted.  Thus,
it is best if range requests start and end on record boundaries.

Selecting the record size most appropriate for a given situation requires a
trade-off.  A smaller record size allows decrypted octets to be released more
rapidly, which can be appropriate for applications that depend on
responsiveness.  Smaller records also reduce the additional data required if
random access into the ciphertext is needed.  Applications that depend on being
able to pad by arbitrary amounts cannot increase the record size beyond 65537
octets.

Applications that don't depending on streaming, random access, or arbitrary
padding can use larger records, or even a single record.  A larger record size
reduces the processing and data overheads.


~~~ drawing
+-----------+--------+-----------+------------+
| salt (16) | rs (4) | idlen (1) | id (idlen) |
+-----------+--------+-----------+------------+
~~~

salt:

: The "salt" parameter comprises the first 16 octets of the "aes128gcm" content
  coding header.  The same "salt" parameter value MUST NOT be reused for two
  different payload bodies that have the same input keying material; generating
  a random salt for every application of the content coding ensures that content
  encryption key reuse is highly unlikely.

rs:

: The "rs" or record size parameter contains an unsigned 32-bit integer in
  network byte order that describes the record size in octets.  Note that it is
  therefore impossible to exceed the 2^36-1 limit on plaintext input to
  AEAD_AES_128_GCM.  Values smaller than 3 are invalid.

keyid:

: The "keyid" parameter can be used to identify the keying material that is
  used.  When the Crypto-Key header field is used, the "keyid" identifies a
  matching value in that field.  The "keyid" parameter MUST be used if keying
  material included in an Crypto-Key header field is needed to derive the
  content encryption key.  The "keyid" parameter can also be used to identify
  keys in an application-specific fashion.


## Content Encryption Key Derivation {#derivation}

In order to allow the reuse of keying material for multiple different HTTP
messages, a content encryption key is derived for each message.  The content
encryption key is derived from the decoded value of the "salt" parameter using
the HMAC-based key derivation function (HKDF) described in {{!RFC5869}} using
the SHA-256 hash algorithm {{FIPS180-4}}.

The value of the "salt" parameter is the salt input to HKDF function.  The
keying material identified by the "keyid" parameter is the input keying material
(IKM) to HKDF.  Input keying material can either be prearranged, or can be
described using the Crypto-Key header field ({{crypto-key}}).  The extract phase
of HKDF therefore produces a pseudorandom key (PRK) as follows:

~~~ inline
   PRK = HMAC-SHA-256(salt, IKM)
~~~

The info parameter to HKDF is set to the ASCII-encoded string "Content-Encoding:
aes128gcm" and a single zero octet:

~~~ inline
   cek_info = "Content-Encoding: aes128gcm" || 0x00
~~~

Note:
: Concatenation of octet sequences is represented by the `||` operator.

AEAD_AES_128_GCM requires a 16 octet (128 bit) content encryption key (CEK), so
the length (L) parameter to HKDF is 16.  The second step of HKDF can therefore
be simplified to the first 16 octets of a single HMAC:

~~~ inline
   CEK = HMAC-SHA-256(PRK, cek_info || 0x01)
~~~


## Nonce Derivation {#nonce}

The nonce input to AEAD_AES_128_GCM is constructed for each record.  The nonce
for each record is a 12 octet (96 bit) value that is produced from the record
sequence number and a value derived from the input keying material.

The input keying material and salt values are input to HKDF with different info
and length parameters.

The length (L) parameter is 12 octets.  The info parameter for the nonce is the
ASCII-encoded string "Content-Encoding: nonce", terminated by a a single zero
octet:

~~~ inline
   nonce_info = "Content-Encoding: nonce" || 0x00
~~~

The result is combined with the record sequence number - using exclusive or - to
produce the nonce.  The record sequence number (SEQ) is a 96-bit unsigned
integer in network byte order that starts at zero.

Thus, the final nonce for each record is a 12 octet value:

~~~ inline
   NONCE = HMAC-SHA-256(PRK, nonce_info || 0x01) XOR SEQ
~~~

This nonce construction prevents removal or reordering of records. However, it
permits truncation of the tail of the sequence (see {{aes128gcm}} for how this
is avoided).


# Crypto-Key Header Field {#crypto-key}

A Crypto-Key header field can be used to describe the input keying material used
in the Encryption header field.

Ordinarily, this header field will not appear in the same message as the
encrypted content.  Including the encryption key with the encrypted payload
reduces the value of using encryption to a somewhat complicated checksum.
However, the Crypto-Key header field could be used in one message to provision
keys for other messages.

The Crypto-Key header field uses the extended ABNF syntax defined in Section 1.2
of {{!RFC7230}} and the `parameter` and `OWS` rules from {{!RFC7231}}.

~~~ abnf7230
  Crypto-Key = #crypto-key-params
  crypto-key-params = [ parameter *( OWS ";" OWS parameter ) ]
~~~

keyid:

: The "keyid" parameter corresponds to the "keyid" parameter in the content
  coding.

aes128gcm:

: The "aes128gcm" parameter contains the base64url-encoded octets {{!RFC7515}} of
  the input keying material for the "aes128gcm" content coding.

Crypto-Key header field values with multiple instances of the same parameter
name in a single crypto-key-params production are invalid.

The input keying material used by the key derivation (see {{derivation}}) can be
determined based on the information in the Crypto-Key header field.

The value or values provided in the Crypto-Key header field is valid only
for the current HTTP message unless additional information indicates a greater
scope.

Alternative methods for determining input keying material MAY be defined by
specifications that use this content coding.  This document only defines the use
of the "aes128gcm" parameter which describes an explicit key.

The "aes128gcm" parameter MUST decode to at least 16 octets in order to be used
as input keying material for "aes128gcm" content coding.


# Examples

This section shows a few examples of the encrypted content coding.

Note: All binary values in the examples in this section use base64url encoding
{{!RFC7515}}.  This includes the bodies of requests.  Whitespace and line
wrapping is added to fit formatting constraints.


## Encryption of a Response {#explicit}

Here, a successful HTTP GET response has been encrypted using input keying
material that is identified by the string "a1".

The encrypted data in this example is the UTF-8 encoded string "I am the
walrus".  The input keying material is included in the Crypto-Key header field.
The content body contains a single record only and is shown here using base64url
encoding for presentation reasons.

~~~ example
HTTP/1.1 200 OK
Content-Type: application/octet-stream
Content-Length: 33
Content-Encoding: aes128gcm
Crypto-Key: aes128gcm=6Aqf1aDH8lSxLyCpoCnAqg

lVIUs_H0A2a8-6dhmzY57H4K4uRFCF6tIIPRO9vrOL6B
~~~

Note that the media type has been changed to "application/octet-stream" to avoid
exposing information about the content.  Alternatively (and equivalently), the
Content-Type header field can be omitted.


## Encryption with Multiple Records

This example shows the same encrypted message, but split into records of 10
octets each.  The first record includes a single additional octet of padding,
which causes the end of the content to align with a record boundary, forcing the
creation of a third record that contains only padding.

~~~ example
HTTP/1.1 200 OK
Content-Length: 70
Content-Encoding: aes128gcm
Crypto-Key: keyid="a1"; aes128gcm="BO3ZVPxUlnLORbVGMpbT1Q"

iBmR5fjBCUvicKLSt1L1GQAAAAoCYTGZvfb0yACNxTo090xk6m_6GwMiLv4AxGSS
_BFGyZS_2z_cOxSHLfuPsAQiId243MTE8B_5Vg-R5OPTNbiV3PlHJcjGONoI
~~~


# Security Considerations

This mechanism assumes the presence of a key management framework that is used
to manage the distribution of keys between valid senders and receivers.
Defining key management is part of composing this mechanism into a larger
application, protocol, or framework.

Implementation of cryptography - and key management in particular - can be
difficult.  For instance, implementations need to account for the potential for
exposing keying material on side channels, such as might be exposed by the time
it takes to perform a given operation.  The requirements for a good
implementation of cryptographic algorithms can change over time.


## Key and Nonce Reuse

Encrypting different plaintext with the same content encryption key and nonce in
AES-GCM is not safe {{!RFC5116}}.  The scheme defined here uses a fixed progression
of nonce values.  Thus, a new content encryption key is needed for every
application of the content coding.  Since input keying material can be reused, a
unique "salt" parameter is needed to ensure a content encryption key is not
reused.

If a content encryption key is reused - that is, if input keying material and
salt are reused - this could expose the plaintext and the authentication key,
nullifying the protection offered by encryption.  Thus, if the same input keying
material is reused, then the salt parameter MUST be unique each time.  This
ensures that the content encryption key is not reused.  An implementation SHOULD
generate a random salt parameter for every message; a counter could achieve the
same result.


## Data Encryption Limits {#limits}

There are limits to the data that AEAD_AES_128_GCM can encipher.  The maximum
record size is 2^36-31 {{!RFC5116}}.  In order to preserve a 2^-40 probability
of indistinguishability under chosen plaintext attack (IND-CPA), the total
amount of plaintext that can be enciphered MUST be less than 2^44.5 blocks
{{AEBounds}}.

If rs is a multiple of 16 octets, this means 398 terabytes can be encrypted
safely, including padding.  However, if the record size is a multiple of 16
octets, the total amount of data that can be safely encrypted is reduced.  The
worst case is a record size of 3 octets, for which at most 74 terabytes of
plaintext can be encrypted, of which at least two-thirds is padding.


## Content Integrity

This mechanism only provides content origin authentication.  The authentication
tag only ensures that an entity with access to the content encryption key
produced the encrypted data.

Any entity with the content encryption key can therefore produce content that
will be accepted as valid.  This includes all recipients of the same HTTP
message.

Furthermore, any entity that is able to modify both the Encryption header field
and the HTTP message body can replace the contents.  Without the content
encryption key or the input keying material, modifications to or replacement of
parts of a payload body are not possible.


## Leaking Information in Headers

Because only the payload body is encrypted, information exposed in header fields
is visible to anyone who can read the HTTP message.  This could expose
side-channel information.

For example, the Content-Type header field can leak information about the
payload body.

There are a number of strategies available to mitigate this threat, depending
upon the application's threat model and the users' tolerance for leaked
information:

1. Determine that it is not an issue. For example, if it is expected that all
   content stored will be "application/json", or another very common media type,
   exposing the Content-Type header field could be an acceptable risk.

2. If it is considered sensitive information and it is possible to determine it
   through other means (e.g., out of band, using hints in other representations,
   etc.), omit the relevant headers, and/or normalize them. In the case of
   Content-Type, this could be accomplished by always sending Content-Type:
   application/octet-stream (the most generic media type), or no Content-Type at
   all.

3. If it is considered sensitive information and it is not possible to convey it
   elsewhere, encapsulate the HTTP message using the application/http media type
   (Section 8.3.2 of {{!RFC7230}}), encrypting that as the payload of the "outer"
   message.


## Poisoning Storage

This mechanism only offers encryption of content; it does not perform
authentication or authorization, which still needs to be performed (e.g., by
HTTP authentication {{?RFC7235}}).

This is especially relevant when a HTTP PUT request is accepted by a server; if
the request is unauthenticated, it becomes possible for a third party to deny
service and/or poison the store.


## Sizing and Timing Attacks

Applications using this mechanism need to be aware that the size of encrypted
messages, as well as their timing, HTTP methods, URIs and so on, may leak
sensitive information.

This risk can be mitigated through the use of the padding that this mechanism
provides.  Alternatively, splitting up content into segments and storing the
separately might reduce exposure. HTTP/2 {{?RFC7540}} combined with TLS
{{?RFC5246}} might be used to hide the size of individual messages.


# IANA Considerations {#iana}

## The "aes128gcm" HTTP Content Coding

This memo registers the "aes128gcm" HTTP content coding in the HTTP Content Codings
Registry, as detailed in {{aes128gcm}}.

* Name: aes128gcm
* Description: AES-GCM encryption with a 128-bit content encryption key
* Reference: this specification


## Encryption Header Fields

This memo registers the "Crypto-Key" HTTP header field in the Permanent
Message Header Registry, as detailed in {{crypto-key}}.

* Field name: Crypto-Key
* Protocol: HTTP
* Status: Standard
* Reference: this specification
* Notes:


## The HTTP Crypto-Key Parameter Registry {#crypto-key-registry}

This memo establishes a registry for parameters used by the "Crypto-Key" header
field under the "Hypertext Transfer Protocol (HTTP) Parameters" grouping.  The
"Hypertext Transfer Protocol (HTTP) Crypto-Key Parameters" operates under an
"Specification Required" policy {{!RFC5226}}.

Entries in this registry are expected to include the following information:

* Parameter Name: The name of the parameter.
* Purpose: A brief description of the purpose of the parameter.
* Reference: A reference to a specification that defines the semantics of the
  parameter.

The initial contents of this registry are:

### keyid

* Parameter Name: keyid
* Purpose: Identify the key that is in use.
* Reference: this document

### aes128gcm {#iana-ekey-aes128gcm}

* Parameter Name: aes128gcm
* Purpose: Provide an explicit input keying material value for the aes128gcm
  content coding.
* Reference: this document


--- back

# JWE Mapping {#jwe}

The "aes128gcm" content coding can be considered as a sequence of JSON Web
Encryption (JWE) objects {{?RFC7516}}, each corresponding to a single fixed size
record that includes leading padding.  The following transformations are applied
to a JWE object that might be expressed using the JWE Compact Serialization:

* The JWE Protected Header is fixed to the value { "alg": "dir", "enc": "A128GCM"
  }, describing direct encryption using AES-GCM with a 128-bit content
  encryption key.  This header is not transmitted, it is instead implied by the
  value of the Content-Encoding header field.

* The JWE Encrypted Key is empty, as stipulated by the direct encryption algorithm.

* The JWE Initialization Vector ("iv") for each record is set to the exclusive
  or of the 96-bit record sequence number, starting at zero, and a value derived
  from the input keying material (see {{nonce}}).  This value is also not
  transmitted.

* The final value is the concatenated JWE Ciphertext and the JWE Authentication
  Tag, both expressed without base64url encoding.  The "." separator is omitted,
  since the length of these fields is known.

Thus, the example in {{explicit}} can be rendered using the JWE Compact
Serialization as:

~~~ example
eyAiYWxnIjogImRpciIsICJlbmMiOiAiQTEyOEdDTSIgfQ..31iQYc1v4a36EgyJ.
VDeU0XxaJkOJDAxPl7h9JD4.VfDeN0aKz-z36T3WWULsBQ
~~~

Where the first line represents the fixed JWE Protected Header, an empty JWE
Encrypted Key, and the algorithmically-determined JWE Initialization Vector.
The second line contains the encoded body, split into JWE Ciphertext and JWE
Authentication Tag.


# Acknowledgements

Mark Nottingham was an original author of this document.

The following people provided valuable input: Richard Barnes, David Benjamin,
Peter Beverloo, Mike Jones, Stephen Farrell, Adam Langley, John Mattsson, Eric
Rescorla, and Jim Schaad.
