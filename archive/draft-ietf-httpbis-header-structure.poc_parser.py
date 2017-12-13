#!/usr/bin/env python

from __future__ import print_function

#######################################################################
# Normally constructed as static table(s) at compile-time

def buildset(l,d):
	s = set()
	for a,b in l:
		for j in range(a, b + 1):
			s.add("%c" % j)
	for c in d:
		s.add(c)
	return s


rfc7230_tchar = buildset(((0x30,0x39), (0x41,0x5a), (0x61,0x7a),),
    "!#$%&'*+-.^_`|~")

rfc7230_ows = buildset([], " \t")

rfc4648_base64 = buildset(((0x30,0x39), (0x41,0x5a), (0x61,0x7a),), "+/")
assert len(rfc4648_base64) == 64
rfc4648_base64.add('=')

h1_string = buildset(((0x20,0x21), (0x23,0x5b), (0x5d,0x7e),), "")
bcp137_hexdig = buildset(( (0x30, 0x39), (0x41, 0x46),), "")

#######################################################################

class Error(Exception):
    """I'm sorry Dave, I cannot do that."""
    pass

# We use a single element list as a "arg-by-reference" to the string we
# are parsing.

def assert_raw(raw):
	assert type(raw) == list and len(raw) == 1 and type(raw[0]) == str

def skip_ows(raw, extra = 0):
	assert_raw(raw)
	s = raw[0][extra:]
	while len(s) > 0 and s[0] in rfc7230_ows:
		s = s[1:]
	raw[0] = s

CS_IDENTIFIER = "IDENTIFIER"
CS_NUMBER = "NUMBER"
CS_INTEGER = "INTEGER"
CS_ASCII_STRING = "ASCII_STRING"
CS_UNICODE_STRING = "UNICODE_STRING"
CS_BLOB = "BLOB"
CS_TIMESTAMP = "TIMESTAMP"

class CSval(object):
	def __init__(self, raw):
		self.canbe = set()
		self.raw = None

		assert_raw(raw)
		skip_ows(raw)
		s = raw[0]
		if len(s) == 0:
			raise Error("CSval expected, have empty string")

		# identifier|integer|number|timestamp
		if s[0] in rfc7230_tchar:
			self.raw, raw[0] = self.get_identifier(s)
			self.canbe.add(CS_IDENTIFIER)

			# XXX: should be done in first pass
			if self.raw[0].isdigit():
				n = 0
			elif self.raw[0] == "-":
				n = 1
			else:
				return

			d = self.raw[n:].find(".")
			if d == 1:
				if self.raw[n:].isdigit() and len(self.raw)<=19:
					self.canbe.add(CS_INTEGER)
				return
			if d == 0 or d >= 14 or not self.raw[n:n+d].isdigit():
				return
			if not self.raw[n+d+1:].isdigit():
				return
			f = len(self.raw) - (n+d+1)
			if f < 1 or f+d > 15:
				return
			self.canbe.add(CS_NUMBER)
			self.canbe.add(CS_TIMESTAMP)
			return

		# h1-ascii-string|h1-unicode-string
		if s[0] == '"':
			u,self.raw,raw[0] = self.get_string(s)
			if u:
				self.canbe.add(CS_UNICODE_STRING)
			else:
				self.canbe.add(CS_ASCII_STRING)
			return

		# h1-blob-string|h1-unicode-string
		if s[0] == ':':
			self.raw,raw[0] = self.get_blob(s)
			self.canbe.add(CS_BLOB)
			return

		raise Error("Cannot parse value")

	def __repr__(self):
		return "<%s '%s'>" % (",".join(self.canbe), self.raw)

	def get_string(self, s):
		j = 1
		b = bytearray(s)
		uc = False
		while b[j] != 0x22:
			if b[j] != 0x5c:
				if s[j] not in h1_string:
					raise Error(
					    "Illegal char (0x%02x)" % b[j])
				j += 1
			elif b[j+1] in (0x5c, 0x22):
				j += 2
			elif b[j+1] != 0x75:
				raise Error("Illegal back-slash escape")
			elif b[j+2] != 0x27:
				raise Error("Illegal back-slash escape")
			else:
				uc = True
				j += 3
				while b[j] != 0x27:
					if s[j] not in bcp137_hexdig:
						raise Error("non-hex unicode")
					j += 1
				j += 1
		return uc,s[:j+1], s[j+2:]

	def get_blob(self, s):
		j = 1
		while s[j] != ':':
			if s[j] not in rfc4648_base64:
				raise Error("Bad base64")
			j += 1
		return s[:j+1], s[j+2:]

	def get_token(self, s):
		t = ""
		while len(s) > 0 and s[0] in rfc7230_tchar:
			t += s[0]
			s = s[1:]
		return t,s

	def get_identifier(self, s):
		t,s = self.get_token(s)
		if len(s) == 0 or s[0] != "/":
			return t,s
		tt, s = self.get_token(s[1:])
		return t + "/" + tt, s


class Cshdr(object):
	def __init__(self, input):
		self.input = input
		self.self_identified = False
		self.dicts = []
		self.parse()

	def parse(self):
		raw = [self.input]
		self.field_name =  CSval(raw)
		if raw[0][0] != ':':
			raise Error("No colon after field-name")
		skip_ows(raw, 1)
		if len(raw[0]) == 0:
			return
		if raw[0][0] == '>':
			if raw[0][-1] != "<":
				raise Error("Missing '<' at end")
			raw[0] = raw[0][:-1]
			self.self_identified = True
			skip_ows(raw, 1)
		while len(raw[0]) > 0:
			dn = CSval(raw)
			dc = {}
			self.dicts.append((dn, dc))
			skip_ows(raw)

			while len(raw[0]) > 0 and raw[0][0] == ";":
				skip_ows(raw, 1)
				kn = CSval(raw)
				skip_ows(raw)
				if len(raw[0]) > 0 and raw[0][0] == "=":
					skip_ows(raw, 1)
					kv = CSval(raw)
					skip_ows(raw)
				else:
					kv = None
				dc[kn] = kv

			if len(raw[0]) == 0:
				break
			if raw[0][0] == ",":
				skip_ows(raw, 1)
				continue
			if raw[0][0] != ";":
				raise Error("Expected EOL, comma or semicolon")
		assert len(raw[0]) == 0

	def dump(self):
		print("Input string:\t\t%s" % self.input)
		print("")
		print("Self-identified:\t%s" % self.self_identified)
		print("Header-name:\t\t%s" % self.field_name)
		for dn,dc in self.dicts:
			print("\tDict\t\t%s" % dn)
			for kn,kv in dc.iteritems():
				print("\t\t\t\t%s: " % kn, kv)


for j in (
	# RFC7231 5.3.2
	"Accept: audio/*; q=0.2, audio/basic",
	"Accept: text/plain; q=0.5, text/html, text/x-dvi; q=0.8, text/x-c",

	# RFC7231 5.3.3
	"Accept-Charset: iso-8859-5, unicode-1-1;q=0.8",

	# RFC7231 5.3.4
	"Accept-Encoding: compress, gzip",
	"Accept-Encoding:",
	"Accept-Encoding: *",
	"Accept-Encoding: compress;q=0.5, gzip;q=1.0",
	"Accept-Encoding: gzip;q=1.0, identity; q=0.5, *;q=0",

	# RFC7231 5.3.5
	"Accept-Language: da, en-gb;q=0.8, en;q=0.7",

	# RFC7234 5.1 [constructed example]
	"Age: 12345",

	# RFC7231 7.4.1
	"Allow: GET, HEAD, PUT",

	# RFC7230 6.1
	"Connection: close",

	# RFC7231 3.1.2.2
	"Content-Encoding: gzip",

	# RFC7231 3.1.3.2
	"Content-Language: da",
	"Content-Language: mi, en",

	# RFC7230 3.3.2
	"Content-Length: 3495",

	# RFC7231 3.1.1.5
	"Content-Type: text/html; charset=ISO-8859-4",

	# RFC7231 5.1.1
	"Expect: 100-continue",

	# RFC7231 5.1.2 [constructed example]
	"Max-Forwards: 34",

	# RFC7231 Appendix A XXX:TODO

	# RFC7230 4.3
	"TE: deflate",
	"TE:",
	"TE: trailers, deflate;q=0.5",

	# RFC7230 4.4 [constructed example]
	"Trailer: Bogo-Header",

	# RFC7230 3.3.1
	"Transfer-Encoding: gzip, chunked",

	# RFC7230 6.7
	"Upgrade: HTTP/2.0, SHTTP/1.3, IRC/6.9, RTA/x11",

	# RFC7231 7.1.4
	"Vary: accept-encoding, accept-language",

	###############################################################
	# Constructed examples
	###############################################################

	# h1-ascii-string
	'cx1: tell-them;txt="foobar"',

	# h1-unicode-string
	'''cx2: tell-them;txt="foobar\u'1F4A9'\u'08'\u'1F574'"''',

	# h1-blob
	'cx3: dont-tell-them;txt=:SGVsbG8gV29ybGQK:',

	'cx4: >dont-tell-them;txt=:SGVsbG8gV29ybGQK: <',

):
	c = Cshdr(j)
	print("-" * 72)
	c.dump()
