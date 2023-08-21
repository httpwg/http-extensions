---
title: Resumable Uploads for HTTP
abbrev: Resumable Uploads
docname: draft-ietf-httpbis-resumable-upload-latest
category: std

ipr: trust200902
area: ART
workgroup: HTTP
keyword: Internet-Draft

stand_alone: yes
smart_quotes: no
pi: [toc, sortrefs, symrefs]

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/resumable-upload
github-issue-label: resumable-upload

author:
  -
    ins: M. Kleidl
    name: Marius Kleidl
    role: editor
    organization: Transloadit Ltd
    email: marius@transloadit.com
  -
    ins: G. Zhang
    name: Guoye Zhang
    role: editor
    organization: Apple Inc.
    email: guoye_zhang@apple.com
  -
    ins: L. Pardue
    name: Lucas Pardue
    role: editor
    organization: Cloudflare
    email: lucaspardue.24.7@gmail.com


normative:
  HTTP: RFC9110

informative:


--- abstract

HTTP clients often encounter interrupted data transfers as a result of canceled requests or dropped connections. Prior to interruption, part of a representation may have been exchanged. To complete the data transfer of the entire representation, it is often desirable to issue subsequent requests that transfer only the remainder of the representation. HTTP range requests support this concept of resumable downloads from server to client. This document describes a mechanism that supports resumable uploads from client to server using HTTP.

--- middle

# Introduction

HTTP clients often encounter interrupted data transfers as a result of canceled requests or dropped connections. Prior to interruption, part of a representation (see {{Section 3.2 of HTTP}}) might have been exchanged. To complete the data transfer of the entire representation, it is often desirable to issue subsequent requests that transfer only the remainder of the representation. HTTP range requests (see {{Section 14 of HTTP}}) support this concept of resumable downloads from server to client.

HTTP methods such as POST or PUT can be used by clients to request processing of representation data enclosed in the request message. The transfer of representation data from client to server is often referred to as an upload. Uploads are just as likely as downloads to suffer from the effects of data transfer interruption. Humans can play a role in upload interruptions through manual actions such as pausing an upload. Regardless of the cause of an interruption, servers may have received part of the representation before its occurrence and it is desirable if clients can complete the data transfer by sending only the remainder of the representation. The process of sending additional parts of a representation using subsequent HTTP requests from client to server is herein referred to as a resumable upload.

Connection interruptions are common and the absence of a standard mechanism for resumable uploads has lead to a proliferation of custom solutions. Some of those use HTTP, while others rely on other transfer mechanisms entirely. An HTTP-based standard solution is desirable for such a common class of problem.

This document defines an optional mechanism for HTTP than enables resumable uploads in a way that is backwards-compatible with conventional HTTP uploads. When an upload is interrupted, clients can send subsequent requests to query the server state and use this information to the send remaining data. Alternatively, they can cancel the upload entirely. Different from ranged downloads, this protocol does not support transferring different parts of the same representation in parallel.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

The terms Byte Sequence, Item, String, Token, Integer, and Boolean are imported from
{{!STRUCTURED-FIELDS=RFC8941}}.

The terms client and server are from {{HTTP}}.

# Overview

Resumable uploads are supported in HTTP through use of a temporary resource, an _upload resource_, that is separate from the resource being uploaded to (hereafter, the _target resource_) and specific to that upload. By interacting with the upload resource, a client can retrieve the current offset of the upload ({{offset-retrieving}}), append to the upload ({{upload-appending}}), and cancel the upload ({{upload-cancellation}}).

The remainder of this section uses an example of a file upload to illustrate different interactions with the upload resource. Note, however, that HTTP message exchanges use representation data (see {{Section 8.1 of HTTP}}), which means that resumable uploads can used with many forms of content -- not just static files.

## Example 1: Complete upload of file with known size

In this example, the client first attempts to upload a file with a known size in a single HTTP request to the target resource. An interruption occurs and the client then attempts to resume the upload using subsequent HTTP requests to the upload resource.

1) The client notifies the server that it wants to begin an upload ({{upload-creation}}). The server reserves the required resources to accept the upload from the client, and the client begins transferring the entire file in the request content.

An informational response can be sent to the client to signal the support of resumable upload on the server and transmit the upload resource URL in the Location header.

~~~
Client                                  Server
|                                            |
| POST                                       |
|------------------------------------------->|
|                                            |
|                                            | Reserve resources
|                                            | for upload
|                                            |------------------
|                                            |                 |
|                                            |<-----------------
|                                            |
|            104 Upload Resumption Supported |
|            with upload resouce URL         |
|<-------------------------------------------|
|                                            |
| Flow Interrupted                           |
|------------------------------------------->|
|                                            |
~~~
{: #fig-upload-creation title="Upload Creation"}

2) If the connection to the server gets interrupted, the client may want to resume the upload. Before this is possible, the client must know the amount of data that the server was able to receive before the connection got interrupted. To achieve this, the client uses Offset Retrieval ({{offset-retrieving}}) to obtain the upload's offset using the upload resource.

~~~
Client                                      Server
|                                                |
| HEAD to upload resource URL                    |
|----------------------------------------------->|
|                                                |
|              204 No Content with Upload-Offset |
|<-----------------------------------------------|
|                                                |
~~~
{: #fig-offset-retrieving title="Offset Retrieval"}

3) Afterwards, the client can resume the upload by sending the remaining file content to the upload resource ({{upload-appending}}), appending to the already stored data in the upload. The `Upload-Offset` value is included to ensure that the client and server agree on the offset that the upload resumes from.

~~~
Client                                       Server
|                                                 |
| PATCH to upload resource URL with Upload-Offset |
|------------------------------------------------>|
|                                                 |
|                      201 Created on completion  |
|<------------------------------------------------|
|                                                 |
~~~
{: #fig-upload-appending title="Upload Append"}

4) If the client is not interested in completing the upload anymore, it can instruct the upload resource to delete the upload and free all related resources ({{upload-cancellation}}).

~~~
Client                                      Server
|                                                |
| DELETE to upload resource URL                  |
|----------------------------------------------->|
|                                                |
|                   204 No Content on completion |
|<-----------------------------------------------|
|                                                |
~~~
{: #fig-upload-cancellation title="Upload Cancellation"}

## Example 2: Upload as a series of parts

In some cases, clients might prefer to upload a file as a series of parts sent serially across multiple HTTP messages. One use case is to overcome server limits on HTTP message content size. Another use case is where the client does not know the final size, such as when file data originates from a streaming source.

This example shows how the client, with prior knowledge about the server's resumable upload support, can upload parts of a file incrementally.

1) If the client is aware that the server supports resumable upload, it can start an upload with the `Upload-Complete: ?0` and the first part of the file.

~~~
Client                                      Server
|                                                |
| POST with Upload-Complete: ?0                  |
|----------------------------------------------->|
|                                                |
|           201 Created with Upload-Complete: ?0 |
|           and Location on completion           |
|<-----------------------------------------------|
|                                                |
~~~
{: #fig-upload-creation-incomplete title="Incomplete Upload Creation"}

2) Afterwards, the following parts are appended ({{upload-appending}}), and the last part of the upload has the `Upload-Complete: ?1` header to indicate the complete transfer.

~~~
Client                                      Server
|                                                |
| PATCH to upload resource URL with              |
| Upload-Offset and Upload-Complete: ?1          |
|----------------------------------------------->|
|                                                |
|                      201 Created on completion |
|<-----------------------------------------------|
|                                                |
~~~
{: #fig-upload-appending-last-chunk title="Upload Append Last Chunk"}

# Upload Creation {#upload-creation}

When a resource supports resumable uploads, the first step is creating the upload resource. To be compatible with the widest range of resources, this is accomplished by adding a header field to the request that initiates the upload, `Upload-Complete`.

As a consequence, resumable uploads support all HTTP request methods that can carry content, such as `POST`, `PUT`, and `PATCH`. Similarly, the response to the upload request can have any response status code. Both the method(s) and status code(s) supported are determined by the resource.

When present, `Upload-Complete` MUST be set to false if the end of the request content is not the end of the upload. Otherwise, it MUST be set to true. This header field can be used for request identification by a server. The request MUST NOT include the `Upload-Offset` header.

If the request is valid, the server SHOULD create an upload resource. Then, the server MUST include the `Location` header in the response and set its value to the URL of the upload resource. The client MAY use this URL for offset retrieval ({{offset-retrieving}}),upload append ({{upload-appending}}), and upload cancellation ({{upload-cancellation}}).

Once the upload resource is available, the target resource MAY send an informational response with `104 (Upload Resumption Supported)` status to the client while the request content is being uploaded. In this informational response, the `Location` header field MUST be set to the upload resource.

The server MUST send the `Upload-Offset` header in the response if it considers the upload active, either when the response is a success (e.g. `201 (Created)`), or when the response is a failure (e.g. `409 (Conflict)`). The value MUST be equal to the end offset of the entire upload, or the begin offset of the next chunk if the upload is still incomplete. The client SHOULD consider the upload failed if the response status code indicates a success but the offset in the `Upload-Offset` header field in the response does not equal to the begin offset plus the number of bytes uploaded in the request.

If the request completes successfully and the entire upload is complete, the server MUST acknowledge it by responding with a successful status code between 200 and 299 (inclusive). Server is RECOMMENDED to use `201 (Created)` response if not otherwise specified. The response MUST NOT include the `Upload-Complete` header with the value of false.

If the request completes successfully but the entire upload is not yet complete indicated by the `Upload-Complete: ?0` header, the server MUST acknowledge it by responding with the `201 (Created)` status code, the `Upload-Complete` header set to false.

If the request includes the `Upload-Complete: ?1` header field and a valid `Content-Length` header field, the client attempts to upload a fixed-length resource in one request. In this case, the upload's final size is the value of the `Content-Length` header field and the server MUST record the upload's final size to ensure its consistency.

~~~ example
:method: POST
:scheme: https
:authority: example.com
:path: /upload
upload-draft-interop-version: 3
upload-complete: ?1
content-length: 100
[content (100 bytes)]

:status: 104
upload-draft-interop-version: 3
location: https://example.com/upload/b530ce8ff

:status: 201
location: https://example.com/upload/b530ce8ff
upload-offset: 100
~~~

~~~ example
:method: POST
:scheme: https
:authority: example.com
:path: /upload
upload-draft-interop-version: 3
upload-complete: ?0
content-length: 25
[partial content (25 bytes)]

:status: 201
location: https://example.com/upload/b530ce8ff
upload-complete: ?0
upload-offset: 25
~~~

If the client received an informational repsonse with the upload URL, it MAY automatically attempt upload resumption when the connection is terminated unexpectedly, or if a server error status code between 500 and 599 (inclusive) is received. The client SHOULD NOT automatically retry if a client error status code between 400 and 499 (inclusive) is received.

File metadata can affect how servers might act on the uploaded file. Clients can send representation metadata (see {{Section 8.3 of HTTP}}) in the request that starts an upload. Servers MAY interpret this metadata or MAY ignore it. The `Content-Type` header can be used to indicate the MIME type of the file. The `Content-Disposition` header can be used to transmit a filename. If included, the parameters SHOULD be either `filename`, `filename*` or `boundary`.

## Feature Detection {#feature-detection}

If the client has no knowledge of whether the resource supports resumable uploads, a resumable request can be used with some additional constraints. In particular, the `Upload-Complete` header field ({{upload-complete}}) MUST NOT be set to false if the server support is unclear. This allows the upload to function as if it is a regular upload.

The server SHOULD send the `104 (Upload Resumption Supported)` informational response to the client, to indicate its support for a resumable upload.

The client MUST NOT attempt to resume an upload if it did not receive the `104 (Upload Resumption Supported)` informational response, and it does not have other signals of whether the server supports resumable uploads.

## Draft Version Identification

> **RFC Editor's Note:**  Please remove this section and `Upload-Draft-Interop-Version` from all examples prior to publication of a final version of this document.

The current interop version is 3.

Client implementations of draft versions of the protocol MUST send a header field `Upload-Draft-Interop-Version` with the interop version as its value to its requests. Its ABNF is

~~~ abnf
Upload-Draft-Interop-Version = sf-integer
~~~

Server implementations of draft versions of the protocol MUST NOT send a `104 (Upload Resumption Supported)` informational response when the interop version indicated by the `Upload-Draft-Interop-Version` header field in the request is missing or mismatching.

Server implementations of draft versions of the protocol MUST also send a header field `Upload-Draft-Interop-Version` with the interop version as its value to the `104 (Upload Resumption Supported)` informational response.

Client implementations of draft versions of the protocol MUST ignore a `104 (Upload Resumption Supported)` informational response with missing or mismatching interop version indicated by the `Upload-Draft-Interop-Version` header field.

The reason both the client and the server are sending and checking the draft version is to ensure that implementations of the final RFC will not accidentally interop with draft implementations, as they will not check the existence of the `Upload-Draft-Interop-Version` header field.

# Offset Retrieval {#offset-retrieving}

If an upload is interrupted, the client MAY attempt to fetch the offset of the incomplete upload by sending a `HEAD` request to the upload resource.

The request MUST NOT include the `Upload-Offset` header or the `Upload-Complete` header. The server MUST reject the request with the `Upload-Offset` header or the `Upload-Complete` header by sending a `400 (Bad Request)` response.

If the server considers the upload resource to be active, it MUST send back a `204 (No Content)` response. The response MUST include the `Upload-Offset` header set to the current resumption offset for the target resource. The response MUST include the `Upload-Complete` header which is set to true if and only if the upload is complete.

An upload is considered complete only if the server completely and successfully received a corresponding creation ({{upload-creation}}) request or append ({{upload-appending}}) request with the `Upload-Complete` header being set to true.

The client MUST NOT perform offset retrieval while creation ({{upload-creation}}) or append ({{upload-appending}}) is in progress.

The offset MUST be accepted by a subsequent append ({{upload-appending}}). Due to network delay and reordering, the server might still be receiving data from an ongoing transfer for the same upload resource, which in the client perspective has failed. The server MAY terminate any transfers for the same upload resource before sending the response by abruptly terminating the HTTP connection or stream. Alternatively, the server MAY keep the ongoing transfer alive but ignore further bytes received past the offset.

The client MUST NOT start more than one append ({{upload-appending}}) based on the resumption offset from a single Offset Retrieval ({{offset-retrieving}}) request.

The response SHOULD include `Cache-Control: no-store` header to prevent HTTP caching.

If the server does not consider the upload resource to be active, it MUST respond with `404 (Not Found)` status code.

The resumption offset can be less than or equal to the number of bytes the client has already sent. The client MAY reject an offset which is greater than the number of bytes it has already sent during this upload. The client is expected to handle backtracking of a reasonable length. If the offset is invalid for this upload, or if the client cannot backtrack to the offset and reproduce the same content it has already sent, the upload MUST be considered a failure. The client MAY cancel the upload ({{upload-cancellation}}) after rejecting the offset.

~~~
:method: HEAD
:scheme: https
:authority: example.com
:path: /upload/b530ce8ff
upload-draft-interop-version: 3

:status: 204
upload-offset: 100
upload-complete: ?0
cache-control: no-store
~~~

The client SHOULD NOT automatically retry if a client error status code between 400 and 499 (inclusive) is received.

# Upload Append {#upload-appending}

Upload appending is used for resuming an existing upload.

The request MUST use the `PATCH` method and be sent to the upload resource. The `Upload-Offset` header field ({{upload-offset}}) MUST be set to the resumption offset.

If the end of the request content is not the end of the upload, the `Upload-Complete` header field ({{upload-complete}}) MUST be set to false.

The server SHOULD respect representation metadata received during creation ({{upload-creation}}) and ignore any representation metadata received from appending ({{upload-appending}}).

If the server does not consider the upload associated with the upload resource active, it MUST respond with `404 (Not Found)` status code.

The client MUST NOT perform multiple upload transfers for the same upload resource in parallel to avoid race conditions and data loss or corruption. The server is RECOMMENDED to take measures to avoid parallel upload transfers: The server MAY terminate any creation ({{upload-creation}}) or append ({{upload-appending}}) for the same upload URL. Since the client is not allowed to perform multiple transfers in parallel, the server can assume that the previous attempt has already failed. Therefore, the server MAY abruptly terminate the previous HTTP connection or stream.

If the offset in the `Upload-Offset` header field does not match the offset provided by the immediate previous offset retrieval ({{offset-retrieving}}), or the end offset of the immediate previous incomplete successful transfer, the server MUST respond with `409 (Conflict)` status code.

The server MUST send the `Upload-Offset` header in the response if it considers the upload active, either when the response is a success (e.g. `201 (Created)`), or when the response is a failure (e.g. `409 (Conflict)`). The value MUST be equal to the end offset of the entire upload, or the begin offset of the next chunk if the upload is still incomplete. The client SHOULD consider the upload failed if the response status code indicates a success but the offset in the `Upload-Offset` header field in the response does not equal to the begin offset plus the number of bytes uploaded in the request.

If the request completes successfully and the entire upload is complete, the server MUST acknowledge it by responding with a successful status code between 200 and 299 (inclusive). Server is RECOMMENDED to use `201 (Created)` response if not otherwise specified. The response MUST NOT include the `Upload-Complete` header with the value of false.

If the request completes successfully but the entire upload is not yet complete indicated by the `Upload-Complete` header, the server MUST acknowledge it by responding with the `201 (Created)` status code, the `Upload-Complete` header set to true.

If the request includes the `Upload-Complete: ?1` header field and a valid `Content-Length` header field, the client attempts to upload the remaining resource in one request. In this case, the upload's final size is the sum of the upload's offset and the `Content-Length` header field. If the server does not have a record of the upload's final size from creation or the previous append, the server MUST record the upload's final size to ensure its consistency. If the server does have a previous record, that value MUST match the upload's final size. If they do not match, the server MUST reject the request with the `400 (Bad Request)` status code.

~~~ example
:method: PATCH
:scheme: https
:authority: example.com
:path: /upload/b530ce8ff
upload-offset: 100
upload-draft-interop-version: 3
content-length: 100
[content (100 bytes)]

:status: 201
upload-offset: 200
~~~

The client MAY automatically attempt upload resumption when the connection is terminated unexpectedly, or if a server error status code between 500 and 599 (inclusive) is received. The client SHOULD NOT automatically retry if a client error status code between 400 and 499 (inclusive) is received.

# Upload Cancellation {#upload-cancellation}

If the client wants to terminate the transfer without the ability to resume, it can send a `DELETE` request to the upload resource. Doing so is an indication that the client is no longer interested in continuing the upload, and that the server can release any resources associated with it.

The client MUST NOT initiate cancellation without the knowledge of server support.

The request MUST use the `DELETE` method. The request MUST NOT include the `Upload-Offset` header or the `Upload-Complete` header. The server MUST reject the request with the `Upload-Offset` header or the `Upload-Complete` header by sending a `400 (Bad Request)` response.

If the server successfully deactivates the upload resource, it MUST send back a `204 (No Content)` response.

The server MAY terminate any in-flight requests to the upload resource before sending the response by abruptly terminating their HTTP connection(s) or stream(s).

If the server does not consider the upload resource to be active, it MUST respond with `404 (Not Found)` status code.

If the server does not support cancellation, it MUST respond with `405 (Method Not Allowed)` status code.

~~~ example
:method: DELETE
:scheme: https
:authority: example.com
:path: /upload/b530ce8ff
upload-draft-interop-version: 3

:status: 204
~~~


# Header Fields

## Upload-Offset

The `Upload-Offset` request and response header field is an Item Structured Header indicating the resumption offset of corresponding upload, counted in bytes. Its value MUST be an integer. Its ABNF is

~~~ abnf
Upload-Offset = sf-integer
~~~

## Upload-Complete

The `Upload-Complete` request and response header field is an Item Structured Header indicating whether the corresponding upload is considered complete. Its value MUST be a boolean. Its ABNF is

~~~ abnf
Upload-Complete = sf-boolean
~~~

The `Upload-Complete` header field MUST only by used if support by the resource is known to the client ({{feature-detection}}).

# Redirection

The `301 (Moved Permanently)` status code and the `302 (Found)` status code MUST NOT be used in offset retrieval ({{offset-retrieving}}) and upload cancellation ({{upload-cancellation}}) responses. For other responses, the upload resource MAY send a `308 (Permanent Redirect)` response which clients SHOULD use for subsequent requests to it. If client receives a `307 (Temporary Redirect)` response to an offset retrieval ({{offset-retrieving}}) request, it MAY apply the redirection directly in an immediate subsequent upload append ({{upload-appending}}).

# Security Considerations

The upload resource URL is the identifier used for modifying the upload. Without further protection of this URL, an attacker may obtain information about an upload, append data to it, or cancel it.

To prevent this, the server SHOULD ensure that only authorized clients can access the upload resource. In addition, the upload resource URL SHOULD be generated in such a way that makes it hard to be guessed by unauthorized clients.

# IANA Considerations

This specification registers the following entry in the Permanent Message Header Field Names registry established by {{!RFC3864}}:

Header field name: Upload-Offset, Upload-Complete

Applicable protocol: http

Status: standard

Author/change controller: IETF

Specification: This document

Related information: n/a

This specification registers the following entry in the "HTTP Status Codes" registry:

Code: 104 (suggested value)

Description: Upload Resumption Supported

Specification: This document

--- back

## Since draft-ietf-httpbis-resumable-upload-01

* Replace Upload-Incomplete header with Upload-Complete.

## Since draft-ietf-httpbis-resumable-upload-00

* Remove Upload-Token and instead use Server-generated upload URL for upload identification.
* Require the Upload-Incomplete header field in Upload Creation Procedure.
* Increase the draft interop version.

## Since draft-tus-httpbis-resumable-uploads-protocol-02

None

## Since draft-tus-httpbis-resumable-uploads-protocol-01

* Clarifying backtracking and preventing skipping ahead during the Offset Receiving Procedure.
* Clients auto-retry 404 is no longer allowed.

## Since draft-tus-httpbis-resumable-uploads-protocol-00

* Split the Upload Transfer Procedure into the Upload Creation Procedure and the Upload Appending Procedure.

# Informational Response

The server is allowed to respond to upload creation ({{upload-creation}}) requests with a `104 (Upload Resumption Supported)` intermediate response as soon as the server has validated the request. This way, the client knows that the server supports resumable uploads before the complete response is received. The benefit is the clients can defer starting the actual data transfer until the server indicates full support (i.e. resumable are supported, the provided upload URL is active etc).

On the contrary, support for intermediate responses (the `1XX` range) in existing software is limited or not at all present. Such software includes proxies, firewalls, browsers, and HTTP libraries for clients and server. Therefore, the `104 (Upload Resumption Supported)` status code is optional and not mandatory for the successful completion of an upload. Otherwise, it might be impossible in some cases to implement resumable upload servers using existing software packages. Furthermore, as parts of the current internet infrastructure currently have limited support for intermediate responses, a successful delivery of a `104 (Upload Resumption Supported)` from the server to the client should be assumed.

We hope that support for intermediate responses increases in the near future, to allow a wider usage of `104 (Upload Resumption Supported)`.

# Feature Detection {#changes-feature-detection}

This specification includes a section about feature detection (it was called service discovery in earlier discussions, but this name is probably ill-suited). The idea is to allow resumable uploads to be transparently implemented by HTTP clients. This means that application developers just keep using the same API of their HTTP library as they have done in the past with traditional, non-resumable uploads. Once the HTTP library gets updated (e.g. because mobile OS or browsers start implementing resumable uploads), the HTTP library can transparently decide to use resumable uploads without explicit configuration by the application developer. Of course, in order to use resumable uploads, the HTTP library needs to know whether the server supports resumable uploads. If no support is detected, the HTTP library should use the traditional, non-resumable upload technique. We call this process feature detection.

Ideally, the technique used for feature detection meets following **criteria** (there might not be one approach which fits all requirements, so we have to prioritize them):

1. Avoid additional roundtrips by the client, if possible (i.e. an additional HTTP request by the client should be avoided).
2. Be backwards compatible to HTTP/1.1 and existing network infrastructure: This means to avoid using new features in HTTP/2, or features which might require changes to existing network infrastructure (e.g. nginx or HTTP libraries)
3. Conserve the user's privacy (i.e. the feature detection should not leak information to other third-parties about which URLs have been connected to)

Following **approaches** have already been considered in the past. All except the last approaches have not been deemed acceptable and are therefore not included in the specification. This follow list is a reference for the advantages and disadvantages of some approaches:

**Include a support statement in the SETTINGS frame.** The SETTINGS frame is a HTTP/2 feature and is sent by the server to the client to exchange information about the current connection. The idea was to include an additional statement in this frame, so the client can detect support for resumable uploads without an additional roundtrip. The problem is that this is not compatible with HTTP/1.1. Furthermore, the SETTINGS frame is intended for information about the current connection (not bound to a request/response) and might not be persisted when transmitted through a proxy.

**Include a support statement in the DNS record.** The client can detect support when resolving a domain name. Of course, DNS is not semantically the correct layer. Also, DNS might not be involved if the record is cached or retrieved from a hosts files.

**Send a HTTP request to ask for support.** This is the easiest approach where the client sends an OPTIONS request and uses the response to determine if the server indicates support for resumable uploads. An alternative is that the client sends the request to a well-known URL to obtain this response, e.g. `/.well-known/resumable-uploads`. Of course, while being fully backwards-compatible, it requires an additional roundtrip.

**Include a support statement in previous responses.** In many cases, the file upload is not the first time that the client connects to the server. Often additional requests are sent beforehand for authentication, data retrieval etc. The responses for those requests can also include a header which indicates support for resumable uploads. There are two options:
- Use the standardized `Alt-Svc` response header. However, it has been indicated to us that this header might be reworked in the future and could also be semantically different from our intended usage.
- Use a new response header `Resumable-Uploads: https://example.org/files/*` to indicate under which endpoints support for resumable uploads is available.

**Send a 104 intermediate response to indicate support.** The clients normally starts a traditional upload and includes a header indicate that it supports resumable uploads (e.g. `Upload-Offset: 0`). If the server also supports resumable uploads, it will immediately respond with a 104 intermediate response to indicate its support, before further processing the request. This way the client is informed during the upload whether it can resume from possible connection errors or not. While an additional roundtrip is avoided, the problem with that solution is that many HTTP server libraries do not support sending custom 1XX responses and that some proxies may not be able to handle new 1XX status codes correctly.

**Send a 103 Early Hint response to indicate support.** This approach is the similar to the above one, with one exception: Instead of a new `104 (Upload Resumption Supported)` status code, the existing `103 (Early Hint)` status code is used in the intermediate response. The 103 code would then be accompanied by a header indicating support for resumable uploads (e.g. `Resumable-Uploads: 1`). It is unclear whether the Early Hints code is appropriate for that, as it is currently only used to indicate resources for prefetching them.

# Upload Metadata

When an upload is created ({{upload-creation}}), the `Content-Type` and `Content-Disposition` header are allowed to be included. They are intended to be a standardized way of communicating the file name and file type, if available. However, this is not without controversy. Some argue that since these headers are already defined in other specifications, it is not necessary to include them here again. Furthermore, the `Content-Disposition` header field's format is not clearly enough defined. For example, it is left open which disposition value should be used in the header. There needs to be more discussion whether this approach is suited or not.

However, from experience with the tus project, users are often asking for a way to communicate the file name and file type. Therefore, we believe it is help to explicitly include an approach for doing so.

# FAQ

* **Are multipart requests supported?** Yes, requests whose content is encoded using the `multipart/form-data` are implicitly supported. The entire encoded content can be considered as a single file, which is then uploaded using the resumable protocol. The server, of course, must store the delimiter ("boundary") separating each part and must be able to parse the multipart format once the upload is completed.

# Acknowledgments
{:numbered="false"}

This document is based on an Internet-Draft specification written by Jiten Mehta, Stefan Matsson, and the authors of this document.

The [tus v1 protocol](https://tus.io/) is a specification for a resumable file upload protocol over HTTP. It inspired the early design of this protocol. Members of the tus community helped significantly in the process of bringing this work to the IETF.

TODO: more acknowledgements.
